using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot : MonoBehaviour
{
    public int robotID = -1;
    Vector3 positionB;
    public int robotSpeed = 5;
    public float rotateSpeed = 30;

    public OptimalRoute optimalRoute;

    public float Yrotation = 0;
    public float targetYrotation = 50;

    public Warehouse warehouse;

    public int closestNodeArrived = -1;
    public int TargetNodeID = -1;

    public int containerCapacity = 5; // Total number of boxes that robot can store in its container
    public int containerFilled = 0; // Number of boxes that are in the robot container

    public bool rightSensorCollision = false;

    public Robot_arm robot_Arm;

    public Warehouse_shelf shelf_target;
    public bool shelf_node_p = true; // true for 1, false for 2

    public bool incZ = false;

    public enum RobotStates{
        Available, OnWayToPick, PickingUp, OnWayToDrop, NotReady
    }

    public RobotStates RobotState = RobotStates.NotReady;

    public Robot_wheels robot_Wheels;

    void Start()
    {
        //positionB = transform.position;

        Yrotation = transform.eulerAngles.y;

        //warehouse = FindObjectOfType(typeof(Warehouse)) as Warehouse;
    }

    public Vector2 get2dvectortransform(Vector3 v3)
    {
        Vector2 v;
        v.x = v3.x;
        v.y = v3.z;

        return v;
    }

    public void gotoClosestNode()
    {
        float mindist = -1;
        Warehouse_node closestNode = null;

        foreach (Warehouse_node node2 in warehouse.nodos)
        {
            float dist = Vector2.Distance(get2dvectortransform(transform.position), get2dvectortransform(node2.transform.position));

            if (closestNode == null || dist < mindist)
            {
                mindist = dist;
                closestNode = node2;
            }
        }

        positionB = closestNode.transform.position;

        closestNodeArrived = closestNode.nodeID;

        Debug.Log("En camino al nodo mas cercano: " + closestNode.transform.position);
    }

    bool wayToClosestNode = false;

    Warehouse_node lastDestination;

    void gotoNode(Warehouse_node node)
    {
        if (lastDestination == null || lastDestination != node)
        {
            if (!wayToClosestNode)
            {
                wayToClosestNode = true;

                gotoClosestNode();
            }
            else
            {
                lastDestination = node;

                positionB = node.transform.position;

                incZ = (positionB.z > transform.position.z) ? true : false;

                TargetNodeID = node.nodeID;

                //Debug.Log("En camino al nodo ubicado en: " + node.transform.position);
            }
        }
    }

    int lastRoutePositionVisited = -1;

    void goToRoute(ArrayList nodesToVisit)
    {

        if (lastRoutePositionVisited == -1)
        {
            //wayToClosestNode = true;
            //gotoClosestNode();
        }
        else if(lastRoutePositionVisited < nodesToVisit.Count)
        {
            int i = 0;
            foreach (int n in nodesToVisit)
            {
                if (i >= lastRoutePositionVisited)
                {
                    gotoNode(warehouse.nodos[n]);
                    Debug.LogWarning("Camino al nodo " + n + " en la posicion de la ruta num " + i);
                    break;
                }
                i++;
            }
        }
    }

    ArrayList nodeRoute = new ArrayList();

    public void createNewRoute(ArrayList r)
    {
        lastRoutePositionVisited = -1;
        nodeRoute = r;
    }

    void calculateTargetYrotation(Vector3 tow)
    {
        Vector2 v2 = get2dvectortransform(transform.position);
        float a = Vector2.Angle(Vector2.right, get2dvectortransform(positionB) - v2) + 90;

        targetYrotation = (int)a;

        if (targetYrotation > 360)
        {
            targetYrotation -= 360;
        }

        if (targetYrotation < 0)
        {
            targetYrotation += 360;
        }

        
        if (incZ)//positionB.z > transform.position.z - 2)
        {
            if (targetYrotation < -177 && targetYrotation > -183)
            {
                targetYrotation += 180;
            }
            else if (targetYrotation > 177 && targetYrotation < 183)
            {
                targetYrotation -= 180;
            }
        }
    }

    void Update()
    {
        if (Vector2.Distance(get2dvectortransform(transform.position), get2dvectortransform(positionB)) <= Time.deltaTime * robotSpeed * 2)
        {
            if (TargetNodeID != -1)
            {
                closestNodeArrived = TargetNodeID;
                TargetNodeID = -1;
            }

            if(lastRoutePositionVisited > nodeRoute.Count)
            {
                robot_Wheels.stop = true;

                //Debug.Log("Robot #" + robotID + " arrived to the end of its route " + closestNodeArrived);
                if (RobotState == RobotStates.OnWayToPick)
                {
                    RobotState = RobotStates.PickingUp;
                    robot_Arm.rotated = 0;
                }
            }

            if(RobotState == RobotStates.NotReady && closestNodeArrived != -1)
            {
                RobotState = RobotStates.Available;
            }

            goToRoute(nodeRoute);
            lastRoutePositionVisited++;

            
        }
        else
        {
            Vector3 tow = Vector3.MoveTowards(transform.localPosition, positionB, Time.deltaTime * robotSpeed);

            calculateTargetYrotation(tow);

            if (targetYrotation > 360)
            {
                targetYrotation -= 360;
            }

            if (targetYrotation < 0)
            {
                targetYrotation += 360;
            }

            if (Yrotation < targetYrotation - 2 || Yrotation > targetYrotation + 2)
            {
                if (RobotState != RobotStates.PickingUp)
                {
                    Quaternion newRotation = Quaternion.Euler(0, targetYrotation, 0);

                    transform.rotation = Quaternion.RotateTowards(transform.rotation, newRotation, rotateSpeed * Time.deltaTime);

                    float ad = Yrotation - targetYrotation;
                    if(ad < 0)
                    {
                        ad *= -1;
                    }
                    if (ad > 25)
                    {
                        robot_Wheels.rotate(rotateSpeed);
                    }
                }

            }
            else
            {
                if (!rightSensorCollision)
                {
                    transform.localPosition = tow;

                    robot_Wheels.goForward(robotSpeed);
                }
            }

            Yrotation = transform.rotation.eulerAngles.y;

            if(Yrotation > 360)
            {
                Yrotation -= 360;
            }

            if(Yrotation < 0)
            {
                Yrotation += 360;
            }

        }

        if (RobotState == RobotStates.PickingUp)
        {
            if (robot_Arm.rotated == 6)
            {
                RobotState = RobotStates.Available;
            }
            else
            {
                if (!robot_Arm.rotating)
                {
                    robot_Arm.rotating = true;

                    if (robot_Arm.rotated == 0)
                    {
                        robot_Arm.setJointSpeed(2, 20);
                        robot_Arm.rotateJoint(0, 0);
                        robot_Arm.rotateJoint(1, -40);
                        robot_Arm.rotateJoint(2, -95);
                    }
                    else if (robot_Arm.rotated == 1)
                    {
                        robot_Arm.enableActuator();
                    }
                    else if (robot_Arm.rotated == 2)
                    {
                        robot_Arm.rotateJoint(0, 0);
                        robot_Arm.rotateJoint(1, 0);
                        robot_Arm.rotateJoint(2, -20);
                    }
                    else if (robot_Arm.rotated == 3)
                    {
                        robot_Arm.rotateJoint(0, 90);
                        robot_Arm.rotateJoint(1, 25);
                        robot_Arm.rotateJoint(2, -120);
                    }
                    else if (robot_Arm.rotated == 4)
                    {
                        robot_Arm.disableActuator();
                    }
                    else if (robot_Arm.rotated == 5)
                    {
                        robot_Arm.setJointSpeed(2, 60);
                        robot_Arm.rotateJoint(0, 90);
                        robot_Arm.rotateJoint(1, 0);
                        robot_Arm.rotateJoint(2, 0);
                    } 
                }
            }
            
        }

    }

}
