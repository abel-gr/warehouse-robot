using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse : MonoBehaviour
{
    public Robot[] robots;
    public Warehouse_node[] nodos;

    public Warehouse_orders warehouse_Orders;

    void getAllRobots()
    {
        robots = FindObjectsOfType(typeof(Robot)) as Robot[];
        Debug.Log(robots.Length + " robots encontrados en el almacen");
    }

    void initializeRobots()
    {
        int i = 0;
        foreach (Robot r in robots)
        {
            r.robotID = i;
            i++;

            r.warehouse = this;
        }
    }

    void getAllNodes()
    {
        nodos = FindObjectsOfType(typeof(Warehouse_node)) as Warehouse_node[];
        Debug.Log(nodos.Length + " nodos encontrados en el almacen");
    }

    void initializeNodes()
    {
        int i = 0;
        foreach (Warehouse_node node2 in nodos)
        {
            node2.nodeID = i;
            i++;
        }
    }

    public void setRobotRoute(int n, int origin, int destination)
    {
        Robot rob = robots[n];

        if (origin == -1)
        {
            origin = rob.closestNodeArrived;
        }

        ArrayList r = rob.optimalRoute.calculateOptimalRoute(nodos[origin], nodos[destination]);
        rob.createNewRoute(r);
    }

    void firstRobotRoute(int robotid, int destination)
    {
        robots[robotid].gotoClosestNode();
        setRobotRoute(robotid, -1, destination);
    }

    void robotsToClosestNodes()
    {
        foreach (Robot robot in robots)
        {
            robot.gotoClosestNode();
        }
    }

    void Start()
    {
        getAllNodes();

        initializeNodes();

        getAllRobots();

        initializeRobots();

        robotsToClosestNodes();

        warehouse_Orders.robotsReady = true;

        /*firstRobotRoute(0, 82);
        firstRobotRoute(1, 138);
        firstRobotRoute(2, 191);
        firstRobotRoute(3, 43);*/
    }

    void Update()
    {
        
    }
}
