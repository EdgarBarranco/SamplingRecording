# SamplingRecording
Python program to record samples from musical instruments.

This program records audio from any source. A prompt is presented asking for the input device to use.
It waits for the audio to reach a certain threshold, then records until the audio goes below the threshold plus a specified amount of time.
It then saves the recording to a file and continues to wait for the next audio to reach the threshold. 
The filename is incremented for each recording with a custom prefix.

## Usage
- Select input device
- Enter the filename prefix
- Enter the threshold. If no threshold is entered, the default is 400
- Enter the time after threshold to stop recording in seconds. If no time is entered, the default is 1

To exit, press Ctrl+C or Q
