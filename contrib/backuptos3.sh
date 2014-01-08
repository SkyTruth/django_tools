#! /bin/bash

MEDIA="$VIRTUAL_ENV/media"
TMP="$VIRTUAL_ENV/media.backup"
S3DIR="s3://skytruthbackups/django_scrapes/"

rm -rf "$TMP"
cp -rl "$MEDIA" "$TMP"
find "$MEDIA" -type f |
  while read name; do
    rm -f "$name"
  done
s3cmd put --recursive --progress "$TMP/"* "$S3DIR"
rm -rf "$TMP"
