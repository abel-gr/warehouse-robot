using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_orders : MonoBehaviour
{
    public Warehouse warehouse;

    public Warehouse_shelf[] shelves;

    public bool robotsReady = false;

    public class OrderInfo
    {
        public Warehouse_node node;
        public int quantity = 0;

        public OrderInfo(Warehouse_node node, int quantity)
        {
            this.node = node;
            this.quantity = quantity;
        }
    }

    public List<OrderInfo> globalOrders = new List<OrderInfo>();

    void getAllShelves()
    {
        shelves = FindObjectsOfType(typeof(Warehouse_shelf)) as Warehouse_shelf[];
        Debug.Log(shelves.Length + " estanterias encontradas en el almacen");
    }

    void initializeShelves()
    {
        int i = 0;
        foreach (Warehouse_shelf r in shelves)
        {
            r.id = i;
            i++;

            r.warehouse_orders = this;
        }
    }

    void basicAssignation(Warehouse_shelf n, Warehouse_node nodo)
    {
        int order_quantity = n.products_to_pick;
        foreach (Robot r in warehouse.robots)
        {
            if (r.RobotState == Robot.RobotStates.Available && r.containerFilled < r.containerCapacity)
            {
                order_quantity = n.products_to_pick;
                if (order_quantity > 0)
                {
                    int canPickup = r.containerCapacity - r.containerFilled;

                    int quantityToPickup = 0;

                    if (order_quantity > canPickup)
                    {
                        quantityToPickup = canPickup;
                        n.products_to_pick = order_quantity - canPickup;
                    }
                    else if (order_quantity == canPickup)
                    {
                        quantityToPickup = canPickup;
                        n.products_to_pick = 0;
                    }
                    else
                    {
                        quantityToPickup = order_quantity;
                        n.products_to_pick = 0;
                    }

                    n.products -= quantityToPickup;

                    r.containerFilled += quantityToPickup;

                    r.shelf_target = n;

                    warehouse.setRobotRoute(r.robotID, -1, nodo.nodeID);
                    r.RobotState = Robot.RobotStates.OnWayToPick;

                }
            }
        }
    }

    public float[] pond = new float[3];

    void Start()
    {
        pond[0] = 0.6f;
        pond[1] = 0.1f;
        pond[2] = 0.05f;

        getAllShelves();
        initializeShelves();
    }


    float calculateMetric(Robot r, Warehouse_shelf n, Warehouse_node nodo, int quantityToPickup)
    {
        float dist = Vector2.Distance(r.get2dvectortransform(r.transform.position), r.get2dvectortransform(nodo.transform.position));
        float filled = r.containerFilled;

        float m = pond[0] * dist + pond[1] * (1/quantityToPickup) + pond[2] * filled;

        return m;
    }

    void improvedAssignation(Warehouse_shelf n, Warehouse_node nodo)
    {
        Robot bestRobotForTask = null;
        float bestMetric = 0;
        int bestRobotquantityToPickup = 0;
        int bestProductstoPick = 0;

        int order_quantity = n.products_to_pick;
        foreach (Robot r in warehouse.robots)
        {
            if (r.RobotState == Robot.RobotStates.Available && r.containerFilled < r.containerCapacity)
            {
                order_quantity = n.products_to_pick;
                if (order_quantity > 0)
                {
                    int canPickup = r.containerCapacity - r.containerFilled;

                    int quantityToPickup = 0;
                    int ProductstoPick = 0;

                    if (order_quantity > canPickup)
                    {
                        quantityToPickup = canPickup;
                        ProductstoPick = order_quantity - canPickup;
                    }
                    else if (order_quantity == canPickup)
                    {
                        quantityToPickup = canPickup;
                        ProductstoPick = 0;
                    }
                    else
                    {
                        quantityToPickup = order_quantity;
                        ProductstoPick = 0;
                    }

                    float metric = calculateMetric(r, n, nodo, quantityToPickup);
                    if (metric < bestMetric || bestRobotForTask == null)
                    {
                        bestRobotquantityToPickup = quantityToPickup;
                        bestMetric = metric;
                        bestRobotForTask = r;
                        bestProductstoPick = ProductstoPick;
                    }
                }
            }
        }

        if (bestRobotForTask != null)
        { 
            n.products -= bestRobotquantityToPickup;
            n.products_to_pick = bestProductstoPick;

            bestRobotForTask.containerFilled += bestRobotquantityToPickup;

            bestRobotForTask.shelf_target = n;

            warehouse.setRobotRoute(bestRobotForTask.robotID, -1, nodo.nodeID);
            bestRobotForTask.RobotState = Robot.RobotStates.OnWayToPick;

            Debug.Log("Robot with best metric for task: " + bestRobotForTask.robotID + " with metric: " + bestMetric);
        }

    }

    void assignationStrategy(int strategy, Warehouse_shelf n, Warehouse_node nodo)
    {
        switch (strategy)
        {
            case 0:
                basicAssignation(n, nodo);
                break;

            case 1:
                improvedAssignation(n, nodo);
                break;
        }
    }

    void assignRobot()
    {
        foreach (Warehouse_shelf n in shelves)
        {
            Warehouse_node nodo = n.node1;

            if (Random.Range(0, 100) > 50)
            {
                nodo = n.node2;
            }

            int order_quantity = n.products_to_pick;

            if (order_quantity > 0)
            {
                assignationStrategy(1, n, nodo);
            }
        }

    }

    public void addOrder(Warehouse_node node, int quantity)
    {
        OrderInfo kv = new OrderInfo(node, quantity);
        globalOrders.Add(kv);
    }

    void Update()
    {
        if (robotsReady)
        {
            assignRobot();
        }
    }
}
