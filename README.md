# Warehouse Robot

## Table of Contents

* [Abstract](#Abstract)
* [Unity Simulation](#Unity-Simulation)
* [Coppelia Simulation](#Coppelia-Simulation)
* [Computer Vision System](#Computer-Vision-System)
* [Website and speech to text to create new orders](#Website-and-speech-to-text-to-create-new-orders)
* [Hardware and 3D design](#Hardware-and-3D-design)

## Abstract

Our robot works around a warehouse moving and organizing inventory. We have done a simulation in Coppelia in which low-level tasks such as the inverse kinematics of the robotic arm and image recognition tasks are seen. We have also implemented a simulation in Unity in which we abstract from those low-level details and focus on showing the operation of a bigger warehouse with many of our robots, working as a swarm so that the tasks are distributed efficiently between all of them.

Each robot is formed by a base capable of moving thanks to a set of wheels. This base carries a structure with an arm. The arm’s job will be to pick up the packages and drop them in a basket structure located rear the arm, so it is able to carry more than one package at the same time. It has a GPS sensor so it is able to know where it is located at every moment, a camera to use computer vision techniques to recognize the texts of the boxes and a remote wifi connection to receive tasks. We also have designed a website where are stored the warehouse orders, and a human worker can add manually and also with his/her own voice orders to be processed by the robots swarm.

In the following sections we explain a summary of the different features of the robot, but more information can be seen in the different pages of the repository wiki.

## Unity Simulation

TODO

## Coppelia Simulation

TODO

## Computer Vision System

TODO

## Website and speech to text to create new orders

TODO

## Hardware and 3D design

TODO
