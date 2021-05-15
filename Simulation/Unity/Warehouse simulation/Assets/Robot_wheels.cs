using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot_wheels : MonoBehaviour
{

    public Transform wheel1;
    public Transform wheel2;
    public Transform wheel3;
    public Transform wheel4;

    public Robot robot;

    public float speed1 = 20;
    public float speed2 = 20;
    public float speed3 = 20;
    public float speed4 = 20;

    public bool stop = false;
    public bool forward_rotate = false; // true for forward, false for rotate

    void Start()
    {
        
    }

    public void goForward(float speed)
    {
        speed1 = -20 * speed;
        speed2 = -20 * speed;
        speed3 = -20 * speed;
        speed4 = -20 * speed;

        forward_rotate = true;
        stop = false;
    }

    public void rotate(float speed)
    {
        speed1 = -3 * speed;
        speed2 = -3 * speed;
        speed3 = 3 * speed;
        speed4 = 3 * speed;

        forward_rotate = false;
        stop = false;
    }

    void Update()
    {
        if (robot.RobotState != Robot.RobotStates.PickingUp && !stop && ((!robot.rightSensorCollision && forward_rotate) | !forward_rotate))
        {
            wheel1.Rotate(new Vector3(0, 0, speed1 * Time.deltaTime));
            wheel2.Rotate(new Vector3(0, 0, speed2 * Time.deltaTime));
            wheel3.Rotate(new Vector3(0, 0, speed3 * Time.deltaTime));
            wheel4.Rotate(new Vector3(0, 0, speed4 * Time.deltaTime));
        }

    }
}
