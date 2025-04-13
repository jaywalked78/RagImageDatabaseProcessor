#!/bin/bash
# Direct ngrok launcher - the simplest possible version

# Just run ngrok directly with the required parameters
exec /snap/bin/ngrok http 7779 --domain=pleasing-strangely-parakeet.ngrok-free.app 