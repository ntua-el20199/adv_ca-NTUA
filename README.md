# Branch Predictor Simulation Project

This repository contains the implementation and evaluation of various branch predictors for processor architecture. The goal is to compare the performance of different branch prediction strategies and understand the impact of key parameters such as entries, associativity, and history length on prediction accuracy.

## Table of Contents
- [Introduction](#introduction)
- [Branch Predictors](#branch-predictors)
  - [Static Predictors](#static-predictors)
  - [Dynamic Predictors](#dynamic-predictors)
  - [Hybrid Predictors](#hybrid-predictors)
- [Simulations](#simulations)
  - [Training vs. Reference Inputs](#training-vs-reference-inputs)
  - [Results](#results)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Introduction

This project explores various branch prediction techniques used in processor architecture. Branch predictors are critical for improving CPU performance by predicting the direction of branches (conditional jumps) before they are executed. Efficient branch prediction reduces pipeline stalls and increases the overall speed of the processor.

## Branch Predictors

The project evaluates the performance of the following branch predictors:

### Static Predictors
- **Always Taken**: A simple static predictor that always predicts a branch will be taken.
- **BTFNT (Backward Taken, Forward Not Taken)**: A static predictor that assumes backward branches are taken and forward branches are not taken.

### Dynamic Predictors
- **N-bit Predictors**: Configurations with different table sizes and associativities (e.g., 8K entries, 2-bit counters).
- **Pentium-M Predictor**: A simple dynamic predictor with a hardware overhead of approximately 30K.
- **Local-History Two-Level Predictors**: Predictors that use local history with different PHT entries and BHT configurations.
- **Global-History Two-Level Predictors**: Predictors that use global history with different BHR lengths and PHT entries.

### Hybrid Predictors
- **Tournament Hybrid Predictors**: A combination of multiple predictors (e.g., local and global) with a meta-predictor that selects between them.

## Simulations

We have performed simulations to compare the performance of the above predictors using both **reference (ref)** and **training (train)** input sets. The metrics used for comparison include the **Misses Per Thousand Instructions (MPKI)** and the **hardware cost** (estimated in terms of entries and associativity).

### Training vs. Reference Inputs

The use of `train` inputs in simulations results in significantly faster execution times, but the key question is whether this affects the conclusions drawn from the performance evaluation of each predictor. We evaluate this by comparing the results of the predictors when using both `ref` and `train` inputs.

### Results

The results of our simulations are discussed in detail, and we provide insights into the best-performing predictors based on different criteria such
