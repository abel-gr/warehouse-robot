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

    public int containerCapacity = 2; // Total number of boxes that robot can store in its container
    public int containerFilled = 0; // Number of boxes that are in the robot container

    public bool rightSensorCollision = false;

    public Robot_arm robot_Arm;

    public Warehouse_shelf shelf_target;
    public bool shelf_node_p = true; // true for 1, false for 2

    public bool incZ = false;

    public Warehouse_node warehousenodeTarget;

    public enum RobotStates{
        Available, OnWayToPick, PickingUp, OnWayToDrop, PrepareUnloading, RampGoingDown, Unloading, RampGoingUp, NotReady
    }

    public RobotStates RobotState = RobotStates.NotReady;

    public Robot_wheels robot_Wheels;

    public DropArea dropArea;
    public Warehouse_node dropNode;

    public Transform ramp;

    public Collider colliderRobot;

    void Start()
    {
        //positionB = transform.position;

        Yrotation = transform.eulerAngles.y;

        dropArea = FindObjectOfType(typeof(DropArea)) as DropArea;
        if(dropArea != null)
        {
            dropNode = dropArea.GetComponentInParent<Warehouse_node>();
        }

        Physics.IgnoreLayerCollision(9, 10);
        Physics.IgnoreLayerCollision(10, 10);
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

    List<Warehouse_box> boxes = new List<Warehouse_box>();

    public void addBox(Warehouse_box b)
    {
        boxes.Add(b);
    }

    bool unloadedBoxes = false;

    public void unloadBoxes()
    {
        foreach (Warehouse_box box in boxes)
        {
            box.enableGravity();
        }

        boxes.Clear();
    }

    void goToDrop()
    {
        if (dropNode != null)
        {
            ArrayList r = optimalRoute.calculateOptimalRoute(warehouse.nodos[closestNodeArrived], dropNode);
            createNewRoute(r);
        }
        else
        {
            RobotState = RobotStates.Available;
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
        if (Vector2.Distance(get2dvectortransform(transform.position), get2dvectortransform(positionB)) <= Time.deltaTime * robotSpeed * 5)
        {
            return;
        }

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

    IEnumerator waitToUnload()
    {
        yield return new WaitForSeconds(0.5f);

        RobotState = RobotStates.RampGoingUp;

        startedWaitingUnload = false;
    }

    const float rampUpRotation = 0.0f;
    const float rampDownRotation = 320.0f;
    Quaternion rampUpQuaternion = Quaternion.Euler(0, 90, rampUpRotation);
    Quaternion rampDownQuaternion = Quaternion.Euler(0, 90, rampDownRotation);
    float rampRotation = 0;
    float rampTargetRotation = 0;
    Quaternion rampTargetQuaternion;
    bool startedWaitingUnload = false;

    void Update()
    {
        if (RobotState == RobotStates.RampGoingDown || RobotState == RobotStates.RampGoingUp)
        {
            robot_Wheels.stop = true;

            rampRotation = ramp.localRotation.eulerAngles.z;

            if (rampRotation < 0)
            {
                rampRotation += 360;
            }
            if (rampRotation >= 360)
            {
                rampRotation -= 360;
            }

            if(RobotState == RobotStates.RampGoingDown)
            {
                rampTargetRotation = rampDownRotation;
                rampTargetQuaternion = rampDownQuaternion;

                if (!unloadedBoxes)
                {
                    unloadedBoxes = true;
                    unloadBoxes();
                }
            }
            else
            {
                rampTargetRotation = rampUpRotation;
                rampTargetQuaternion = rampUpQuaternion;
            }

            if (rampRotation > rampTargetRotation - 2 && rampRotation < rampTargetRotation + 2)
            {
                RobotState = (RobotState == RobotStates.RampGoingDown) ? RobotStates.Unloading : RobotStates.Available;
            }
            else
            {
                ramp.localRotation = Quaternion.RotateTowards(ramp.localRotation, rampTargetQuaternion, 9.0f * Time.deltaTime);
            }
        }
        else if (RobotState == RobotStates.Unloading)
        {
            robot_Wheels.stop = true;

            containerFilled = 0;

            if (!startedWaitingUnload)
            {
                startedWaitingUnload = true;
                unloadedBoxes = false;
                StartCoroutine(waitToUnload());
            }
        }
        else
        {

            if (RobotState != RobotStates.PrepareUnloading && Vector2.Distance(get2dvectortransform(transform.position), get2dvectortransform(positionB)) <= Time.deltaTime * robotSpeed * 2)
            {
                if (TargetNodeID != -1)
                {
                    closestNodeArrived = TargetNodeID;
                    TargetNodeID = -1;
                }

                if (lastRoutePositionVisited > nodeRoute.Count)
                {
                    robot_Wheels.stop = true;

                    //Debug.Log("Robot #" + robotID + " arrived to the end of its route " + closestNodeArrived);
                    if (RobotState == RobotStates.OnWayToPick)
                    {
                        if (warehousenodeTarget.nodeID == closestNodeArrived)
                        {
                            RobotState = RobotStates.PickingUp;
                            robot_Arm.rotated = 0;

                            if (Warehouse_training.trainingMode)
                            {
                                Warehouse_training.robotsFinished++;
                            }
                        }
                        else
                        {
                            if (optimalRoute.bestRoute.Count == 0)
                            {
                                RobotState = RobotStates.Available;
                            }
                        }
                    }
                    else if (RobotState == RobotStates.OnWayToDrop)
                    {
                        RobotState = RobotStates.PrepareUnloading;
                    }
                }

                if (RobotState == RobotStates.NotReady && closestNodeArrived != -1)
                {
                    RobotState = RobotStates.Available;
                }

                goToRoute(nodeRoute);
                lastRoutePositionVisited++;


            }
            else
            {
                Vector3 tow = Vector3.MoveTowards(transform.localPosition, positionB, Time.deltaTime * robotSpeed);

                if (RobotState == RobotStates.PrepareUnloading)
                {
                    targetYrotation = 0;
                }
                else
                {
                    calculateTargetYrotation(tow);
                }

                if (targetYrotation > 359)
                {
                    targetYrotation -= 360;

                }
                else if (targetYrotation < 0)
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
                        if (ad < 0)
                        {
                            ad *= -1;
                        }
                        if (ad > 15)
                        {
                            robot_Wheels.rotate(rotateSpeed);
                        }
                    }

                }
                else
                {
                    if (RobotState == RobotStates.PrepareUnloading)
                    {
                        RobotState = RobotStates.RampGoingDown;
                    }
                    else
                    {

                        robot_Wheels.forward_rotate = true;

                        if (!rightSensorCollision)
                        {
                            transform.localPosition = tow;

                            robot_Wheels.goForward(robotSpeed);
                        }
                    }
                }

                Yrotation = transform.rotation.eulerAngles.y;

                if (Yrotation > 359)
                {
                    Yrotation -= 360;

                }
                else if (Yrotation < 0)
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
                            robot_Arm.rotateJoint(1, 20);
                            robot_Arm.rotateJoint(2, -140);
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
            else if (RobotState == RobotStates.Available)
            {
                if (containerCapacity == containerFilled)
                {
                    RobotState = RobotStates.OnWayToDrop;
                    goToDrop();
                }
            }
        }
    }

    void OnCollisionEnter(Collision collision)
    {
        Warehouse_box r = collision.gameObject.GetComponent<Warehouse_box>();

        if (r != null)
        {
            Physics.IgnoreCollision(collision.collider, colliderRobot);
        }
    }

}
