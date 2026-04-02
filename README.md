<p align='center'>
  <a href='https://praig.ua.es/'><img src='https://i.imgur.com/Iu7CvC1.png' alt='PRAIG-logo' width='100'></a>
</p>

<h1 align='center'>TriScore Dataset</h1>


<p align='center'>
  <a href='#about'>About</a> •
  <a href='#how-to-use'>How To Use</a> •
  <a href='#citations'>Citations</a> •
  <a href='#acknowledgments'>Acknowledgments</a> •
  <a href='#references'>References</a>
</p>

## About

This repository provides the tools and utilities to pre-process and generate **TriScore**, a tri-modal dataset designed for classification and retrieval tasks, presented in the paper:  **TriScore: Aligning Audio, Symbolic Scores, and Sheet Music Images in a Shared Embedding Space**. The dataset is built from *MUSCAT: a Multimodal mUSic Collection for Automatic Transcription of real recordings and image scores* [1]. The [original dataset](https://grfia.dlsi.ua.es/muscat/) can be downloaded upon request through a form. This repository hosts the tools to **generate the score images** from the MUSCUTS sub-set kern-encoded scores and to **retrieve metadata** (composer, instruments, etc.) for each fragment in the sub-set.

## How To Use

**Script**: `process_dataset.py`

**Arguments**: 
- `--ds_dir`: The folder containing the MUSCUTS collection (`/MUSCUTS` when downloading the dataset).
- `--metadata_json_dir`: The folder containing the exported json collections with the metadata. (`/keys`).
- `--log_dir`: Folder to log if any errors occur (`/log`).

The dependencies are specified in the [`Dockerfile`](Dockerfile) and [`requirements.txt`](requirements.txt).


## Citations

```bibtex
    YET TO BE PUBLISHED
```

## Acknowledgments

This research was supported by the Spanish Ministry of Science and Innovation through the LEMUR research project (PID2023-148259NB-I00), funded by MCIU/AEI/10.13039/501100011033/FEDER, EU, and the European Social Fund Plus (FSE+).

<p align="center">
    <a href="https://praig.ua.es/category/research/projects/"><img src="https://raw.githubusercontent.com/lemur-project/acknowledgments/refs/heads/main/infographics/lemur_logo.png" alt="LEMUR logo" height="60"></a>
    <a href="https://www.aei.gob.es/"><img src="https://raw.githubusercontent.com/lemur-project/acknowledgments/refs/heads/main/infographics/acknowledgements.png" alt="Ministry Logo, European Union Flag and Statal Research Agency Logo" height="60"></a>
    <br>
</p>

## References

[1] Alejandro Galan-Cuenca, Jose J. Valero-Mas, Juan C. Martinez-Sevilla, Antonio Hidalgo-Centeno, Antonio Pertusa, and Jorge Calvo-Zaragoza. 2024. MUSCAT: A Multimodal mUSic Collection for Automatic Transcription of Real Recordings and Image Scores. In Proceedings of the 32nd ACM International Conference on Multimedia (MM '24). Association for Computing Machinery, New York, NY, USA, 583–591. https://doi.org/10.1145/3664647.3681572

