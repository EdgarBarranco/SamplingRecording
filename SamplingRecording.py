import os
import queue
import threading
import time
import wave

import numpy as np
import pyaudio # PyAudio provides Python bindings for PortAudio, the cross-platform audio I/O library

class AudioRecorder:
    CHUNK = 4096
    FORMAT = pyaudio.paInt16  # 16 bit
    CHANNELS = 1 # Number of audio channels (1 = mono) (2 = stereo)
    RATE = 44100 # 44.1 kHz

    def __init__(self, device_index=None, filename=None, threshold=400, time_at=1):
        self._stream = None
        self._q = queue.Queue()
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._record)
        self._device_index = device_index
        self._filename = filename
        self.THRESHOLD = threshold
        self.TIME_AT = time_at


    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

    def _record(self):
        p = pyaudio.PyAudio()
        self._stream = p.open(format=self.FORMAT,
                              channels=self.CHANNELS,
                              rate=self.RATE,
                              input=True,
                              input_device_index=self._device_index,
                              frames_per_buffer=self.CHUNK)

        frames = []
        recording = False
        while not self._stop_event.is_set():
            data = self._stream.read(self.CHUNK)
            self._q.put(data)

            # check if audio signal is above threshold
            audio_signal = np.abs(np.frombuffer(data, dtype=np.int16)).max()
            if audio_signal > self.THRESHOLD:
                recording = True

            # start recording if audio signal is detected
            if recording:
                frames.append(data)

            # stop recording if audio signal is below threshold for more than 1 second
            if recording and audio_signal < self.THRESHOLD:
                time.sleep(self.TIME_AT)
                data = self._stream.read(self.CHUNK)
                audio_signal = np.abs(np.frombuffer(data, dtype=np.int16)).max()
                if audio_signal < self.THRESHOLD:
                    time.sleep(self.TIME_AT)
                    filename = self._get_filename()
                    self._save_file(frames, filename)
                    frames = []
                    recording = False

        self._stream.stop_stream()
        self._stream.close()
        p.terminate()

    def _get_filename(self):
        if not os.path.exists('audio'):
            os.makedirs('audio')
        i = 0
        while True:
            filename = f'audio/{self._filename}_{i}.wav'
            if not os.path.exists(filename):
                return filename
            i += 1

    def _save_file(self, frames, filename):
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        print(f'Saved as {filename}')


if __name__ == '__main__':
    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    print(f'Available input devices: {device_count}')

    for i in range(device_count):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            print(f'Device {i}: {device_info["name"]}')

    device_index = int(input('Select input device: '))
    filename = input('Enter filename: ')
    threshold = input('Enter threshold (400): ')
    if threshold.isdigit():
        threshold = int(threshold)
    else:
        threshold = 400
    time_at = input('Enter seconds to record after threshold (1): ')
    if time_at.isdigit():
        time_at = int(time_at)
    else:
        time_at = 1

    recorder = AudioRecorder(device_index=device_index, filename=filename, threshold=threshold, time_at=time_at)
    recorder.start()

    while True:
        try:
            user_input = input('Press q to quit\n')
            if user_input == 'q':
                recorder.stop()
                break
        except KeyboardInterrupt:
            recorder.stop()
            break
