using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot_arm : MonoBehaviour
{
    public enum JointAxis
    {
        X, Y, Z
    }

    public GameObject[] joints;
    public JointAxis[] joints_axis;
    public int[] minAngles;
    public int[] maxAngles;
    public int[] rotateSpeed;

    public int[] targetAngles;

    public bool rotating = false;
    public int rotated = 0;

    public Robot_actuator actuator;

    List<Quaternion> quaternions = new List<Quaternion>();

    float getJointRotation(int id)
    {
        if(joints_axis[id] == JointAxis.X)
        {
            return joints[id].transform.localRotation.eulerAngles.x;
        }
        else if (joints_axis[id] == JointAxis.Y)
        {
            return joints[id].transform.localRotation.eulerAngles.y;
        }
        else
        {
            return joints[id].transform.localRotation.eulerAngles.z;
        }
    }

    Quaternion JointQuaternion(int id, float angle)
    {
        Quaternion newRotation = Quaternion.Euler(0, 0, 0);

        if (id >= 0 && id < joints.Length)
        {
            
            if (joints_axis[id] == JointAxis.X)
            {
                newRotation = Quaternion.Euler(angle, 0, 0);
            }
            else if (joints_axis[id] == JointAxis.Y)
            {
                newRotation = Quaternion.Euler(0, angle, 0);
            }
            else
            {
                newRotation = Quaternion.Euler(0, 0, angle);
            }
        }

        return newRotation;
    }

    public void setJointSpeed(int id, int speed)
    {
        if (id >= 0 && id < rotateSpeed.Length)
        {
            rotateSpeed[id] = speed;
        }
    }

    public void rotateJoint(int id, float angle)
    {

        if (angle < 0)
        {
            angle += 360;
        }
        if (angle > 360)
        {
            angle -= 360;
        }

        Quaternion newRotation = JointQuaternion(id, angle);
        quaternions[id] = newRotation;
        targetAngles[id] = (int)angle;
    }

    public void enableActuator()
    {
        actuator.enableActuator();
    }

    public void disableActuator()
    {
        actuator.disableActuator();
    }

    void Start()
    {
        foreach(GameObject g in joints)
        {
            quaternions.Add(Quaternion.Euler(0, 0, 0));
        }
    }

    public int id = 0;
    public int rotatedN = 0;
    void Update()
    {
        if (rotating)
        {
            id = 0;
            rotatedN = 0;
            foreach (GameObject g in joints)
            {

                int targetRotation = targetAngles[id];
                int rotation = (int)getJointRotation(id);
                Transform jointtransfom = g.transform;
                Quaternion newRotation = quaternions[id];
                int speed = rotateSpeed[id];

                if(rotation < 0)
                {
                    rotation += 360;
                }
                if (rotation > 360)
                {
                    rotation -= 360;
                }

                if (rotation > targetRotation - 2 && rotation < targetRotation + 2)
                {
                    rotatedN++;
                }
                else
                {
                    jointtransfom.localRotation = Quaternion.RotateTowards(jointtransfom.localRotation, newRotation, speed * Time.deltaTime);
                    rotation = (int)getJointRotation(id);

                    //Debug.Log("ID: " + id + " rot:" + rotation + " target: " + targetRotation + " quat: (x: " + newRotation.x + ",y: " + newRotation.y + ",z: " + newRotation.z + ")");
                }

                id++;
            }

            if(rotatedN == id)
            {
                rotated++;
                rotating = false;
            }
        }
    }
}
