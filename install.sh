#!/bin/sh
# Install the themes for the current user; select them in Fcitx5 afterwards.
set -eu

if [ "$#" -ne 0 ]; then
    printf 'Usage: %s\n' "$0" >&2
    exit 2
fi

source_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
themes_dir=${XDG_DATA_HOME:-"$HOME/.local/share"}/fcitx5/themes

for theme in win11-light win11-dark win11-vermilion win11-vermilion-dark; do
    mkdir -p -- "$themes_dir/$theme"
    cp -- "$source_dir/$theme/theme.conf" "$source_dir/$theme/"*.svg "$themes_dir/$theme/"
done

printf 'Installed Windows 11 Light, Dark, Vermilion and Vermilion Dark to %s\n' "$themes_dir"
printf 'Select the themes in Fcitx5 Configuration > Addons > Classic User Interface.\n'
