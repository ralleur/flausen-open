    property var weatherFrames: []
    property real weatherLastFrame: 0
    property bool weatherSampling: false
    Connections {
        target: root.contentItem.Window.window
        function onFrameSwapped(): void {
            if(!root.weatherSampling)return;
            const now=Date.now();if(root.weatherLastFrame)root.weatherFrames.push(now-root.weatherLastFrame);
            root.weatherLastFrame=now;
        }
    }
    TestCase { id: weatherTest; name: "WeatherPointer"; when: false }
    IpcHandler {
        target: "weatherTest-" + root.screen.name
        function open(): void {
            panels.popouts.currentName="weather";
            panels.popouts.currentCenter=root.width-200;
            panels.popouts.hasCurrent=true;
        }
        function close(): void {panels.popouts.hasCurrent=false;}
        function sample(extraBlur:bool): void {
            panels.popoutsWrapper.weatherPoolForTest.suspended=!extraBlur;
            root.weatherFrames=[];root.weatherLastFrame=0;root.weatherSampling=true;
        }
        function frames(): string {root.weatherSampling=false;return JSON.stringify(root.weatherFrames);}
        function pool(): string {
            const p=panels.popoutsWrapper.weatherPoolForTest;
            return JSON.stringify({passes:p.pooledPassCount,width:p.capacityWidth,height:p.capacityHeight,active:p.activePassCount});
        }
        function inspect(): string {
            const current=panels.popouts.current;
            function walk(item) {
                const p=item.mapToItem(root.contentItem,0,0);
                let result={type:item.toString(),name:item.objectName,x:p.x,y:p.y,width:item.width,height:item.height};
                if(item.text!==undefined)result.text=item.text;
                result.children=(item.children||[]).map(walk);return result;
            }
            return JSON.stringify({open:panels.popouts.hasCurrent,current:current?walk(current):null,
                offset:current?.hourOffset,maxOffset:current?.maxOffset,expanded:current?.hourlyExpanded,
                scale:current?.scaleOffset,fontScale:current?.fontScale,
                data:{city:Weather.city,hasWeather:Weather.hasWeather,hours:Weather.hourlyForecast?.length},
                popout:{x:panels.popoutsWrapper.x+panels.leftMargin,y:panels.popoutsWrapper.y+panels.topMargin,width:panels.popoutsWrapper.width,height:panels.popoutsWrapper.height}});
        }
        function scenario(name:string): void {
            const current=panels.popouts.current;
            current.fontScale=name==="large"?1.7:1.15;
            current.width=name==="narrow"?300:440*current.scaleOffset;
            current.hourOffset=0;
            current.hourlyExpanded=true;
            current.weather=Weather;
            if(name==="empty")current.weather={city:"",loc:"",hasWeather:false,loading:false,hourlyForecast:[],icon:"cloud"};
            if(name==="flat" || name==="rain")current.weather={city:"Köln",hasWeather:true,loading:false,temp:"12°C",tempC:12,
                description:"Partly cloudy",maxTemp:"12°",minTemp:"6°",feelsLike:"7°C",humidity:54,windSpeed:0,icon:"partly_cloudy_day",
                hourlyForecast:Array.from({length:9},(_,i)=>({tempC:12,hour:15+i,timestamp:"2026-11-04T"+String(15+i).padStart(2,"0")+":00",precipChance:name==="rain"?45:0,icon:name==="rain"?"rainy":"clear_day"}))};
        }
        function pointer(kind:string,x:real,y:real): void {
            if(kind==="click")weatherTest.mouseClick(root.contentItem,x,y,Qt.LeftButton);
            else weatherTest.mouseMove(root.contentItem,x,y);
        }
    }

