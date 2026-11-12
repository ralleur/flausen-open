import QtQuick
import QtTest
import qs.services

Item {
    id: testRoot
    required property Item audio
        TestCase {
            id: interactionTests
            name: "AudioControls"
            when: windowShown
            function test_interactions() {
                const audio = testRoot.audio;
                const out = findChild(audio, "audioOutputVolume");
                const input = findChild(audio, "audioInputVolume");
                verify(out !== null && input !== null);
                mouseClick(out, out.width/2, out.height*0.25);
                verify(Math.abs(Audio.volume - 0.75) < 0.02);
                mousePress(out, out.width/2, out.height*0.75);
                mouseMove(out, out.width/2, out.height*0.1);
                mouseRelease(out, out.width/2, out.height*0.1);
                verify(Math.abs(Audio.volume - 0.9) < 0.02);
                const beforeWheel = Audio.volume;
                mouseWheel(out, out.width/2, out.height/2, 0, -120);
                verify(Audio.volume < beforeWheel);
                keyClick(Qt.Key_Home);
                compare(Audio.volume, 0);
                keyClick(Qt.Key_End);
                compare(Audio.volume, 1);
                keyClick(Qt.Key_Down);
                verify(Audio.volume < 1 && Audio.volume > 0.8);
                mouseClick(input, input.width/2, input.height*0.6);
                verify(Math.abs(Audio.sourceVolume - 0.4) < 0.02);
                const before = Audio.source.audio.muted;
                const mute = findChild(audio, "audioInputMute");
                mouseClick(mute, mute.width/2, mute.height/2);
                compare(Audio.source.audio.muted, !before);
                mouseClick(mute, mute.width/2, mute.height/2);
                compare(Audio.source.audio.muted, before);
                const selector = findChild(audio, "audioOutputDevice");
                mouseClick(selector, selector.width/2, selector.height/2);
                compare(audio._outputsOpen, true);
                wait(100);
                const other = findChild(audio, "audioDeviceChoice-2");
                verify(other !== null);
                mouseClick(other, other.width/2, other.height/2);
                compare(Audio.sink.nodeId, 2);
                compare(audio._outputsOpen, false);
                mouseClick(selector, selector.width/2, selector.height/2);
                compare(audio._outputsOpen, true);
                mouseClick(selector, selector.width/2, selector.height/2);
                compare(audio._outputsOpen, false);
                const sections = [...audio.children].filter(c => c.expanded !== undefined);
                compare(sections.length, 2);
                for (const section of sections) {
                    mouseClick(section, section.width / 2, 15);
                    compare(section.expanded, true);
                    wait(150);
                    mouseClick(section, section.width / 2, 15);
                    compare(section.expanded, false);
                }
                console.log("AUDIO_INTERACTIONS_PASS", JSON.stringify({drag:true,click:true,keyboard:true,mute:true,deviceToggle:true,deviceSwitch:true,wheel:true,sections:true}));
            }
        }
    Timer {
        interval: 300
        running: true
        onTriggered: interactionTests.test_interactions()
    }
}
