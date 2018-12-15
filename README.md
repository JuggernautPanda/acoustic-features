# Acoustic Event Detection with STM32L4/Keras/TensorFlow

![](./oscilloscope/screenshots/spectrogram(psd)_small.jpg)

## Background and motivation

I am just interested in Acoustic Event Detection (AED) on "edge AI": ["New Architectures Bringing AI to the Edge"](https://www.eetimes.com/document.asp?doc_id=1333920).

## Project status (Dec 15, 2018)

- All the pre-processing features and the oscilloscope GUI have been implemented.
- Several CNN models on Keras/TensorFlow have already been tested.
- Inference engine based on Keras/TensorFlow has been implemented for Win10 and RasPi3.
- Working on beam forming with LPF to flatten the frequency response in Endfire mode.

## AED system

Architecture:

```
                                          *** pre-processing ***             *** inference (*1) ***
                                          ARM Cortex-M4(STM32L476RG)        Another core of ARM Cortex-M
                                      .................................... .............................
                                      :   Filters for feature extraction : :    Inference on CNN       :
Sound/voice ))) [MEMS mic]--PDM-->[DFSDM]--+->[]->[]->[]->[]---+----Features-->[CubeMX.AI or CMSIS-NN] :
                                      :    |                   |         : :                           :
                                      :    +------------+      |         : :                           :
                                      :     +-----------|------+         : :                           :
                                      :     |           |                : :                           :
                                      :     V           V                : :                           :
                                      :..[USART]......[DAC]..............: :...........................:
                                            |           |
                                            |           | *** monitoring ***
                                            |           +---> [Analog filter] --> head phone
                                       (features)
                                            |
                                            | *** learning ***
                                            +---> [oscilloscope.py/Win10 or RasPi3] --- (data set) ---> Keras/TensorFlow
                                            |
                                            | *** inference ***
                                            +---> [oscilloscope.py/Win10 or RasPi3]
```

*1 CubeMX.AI will be available in 1Q/2019: https://community.st.com/s/question/0D50X00009yG1AUSA0/when-is-stm32cubeai-available

Platform:
- [Platform and tool chain](./PLATFORM.md)

## System components

- [Edge device for deep learning (CubeMX/TrueSTUDIO)](./stm32)
- [Arduino shield of two MEMS microphones with beam forming support (KiCAD)](./kicad)
- [Oscilloscope GUI implementation on matplotlib/Tkinter (Python)](./oscilloscope)

## Use cases of AED on edge AI

I apply the system to potential edge AI use cases:
- musical instrument recognition and music performance analysis
- human activity recognition
- always-on automatic speech recogniton (e.g., "OK Google")
- automatic questionnaire collection in a restaurant
- bird recognition

### CNN experiments (learning and inference)

![](./oscilloscope/screenshots/ml_inference_classical_guitar.jpg)

- [CNN experiments with Keras/TensorFlow](./tensorflow)
