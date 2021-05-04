using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot_rightSensor : MonoBehaviour
{

    public Robot robot;

    void Start()
    {
        
    }

    void Update()
    {
        
    }

    void OnTriggerEnter(Collider collider)
    {
        Robot r = collider.gameObject.GetComponent<Robot>();
        if (r != null)
        {
            robot.rightSensorCollision = true;
        }
    }

    void OnTriggerExit(Collider collider)
    {
        Robot r = collider.gameObject.GetComponent<Robot>();
        if (r != null)
        {
            robot.rightSensorCollision = false;
        }
    }
}
