#!/bin/sh


README="README.md"
SAVE_FILE="${README}.orig"

save() {
    cp "$README" "$SAVE_FILE"
    echo "Backup file saved to $SAVE_FILE"
}

generate_docs() {

    echo "Regenerating documentation"

    PYTHONPATH=./ poetry run settings-doc generate \
    --class service_kit.configuration.ServiceConfiguration \
    --output-format markdown \
    --update README.md \
    --between "<!-- generated env. vars. start -->" "<!-- generated env. vars. end -->" \
    --heading-offset 3

    return $?
}

restore() {
    echo "Generation failed. Restoring saved file $SAVE_FILE"
    rm "$README"
    cp "$SAVE_FILE" "$README"
}

cleanup() {
    echo "Cleaning up"
    echo "Removing save file $SAVE_FILE"
    rm "$SAVE_FILE"
}


save && (generate_docs || restore)
cleanup
