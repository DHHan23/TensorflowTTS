from pathlib import Path
from tqdm import tqdm
from pydub import AudioSegment

mcv_path = Path('.') / 'mcv' / 'eo'
clips_path = mcv_path / 'clips'

datasets_path = Path('.') / 'datasets'
wavs_path = datasets_path / 'wavs'

names = []
for path in tqdm(clips_path.glob('*.mp3')):
    name = path.stem
    sound = AudioSegment.from_mp3(str(path))
    sound = sound.set_channels(1)
    sound = sound.set_frame_rate(22050)
    sound.export(str(wavs_path / name) + '.wav', format="wav")
    names.append(name)

print(f"Generating metadata.csv...")
with open(datasets_path / 'metadata-mcv.csv', 'w', encoding='utf8') as metadata:
    for name in names:
        metadata.write(f'{name}|\n')