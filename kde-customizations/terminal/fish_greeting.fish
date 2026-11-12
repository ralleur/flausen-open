function fish_greeting
    if isatty stdout; and command -q python3
        set -l data_home "$HOME/.local/share"
        if set -q XDG_DATA_HOME; and test -n "$XDG_DATA_HOME"
            set data_home "$XDG_DATA_HOME"
        end
        python3 "$data_home/flausen-terminal/flausen.py" --system-info --static
    else
        command -v fastfetch &> /dev/null && fastfetch --key-padding-left 5
    end
end
