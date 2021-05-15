using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_orders : MonoBehaviour
{
    public Warehouse warehouse;

    public Warehouse_shelf[] shelves;

    public bool robotsReady = false;

    public Warehouse_training warehouse_Training;

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

        if (Warehouse_training.trainingMode)
        {
            warehouse_Training.startTrainingIteration();
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
                    r.warehousenodeTarget = nodo;

                    warehouse.setRobotRoute(r.robotID, -1, nodo.nodeID);
                    r.RobotState = Robot.RobotStates.OnWayToPick;

                }
            }
        }
    }

    public struct formulaWeights
    {
        public float distance;
        public float quantityToPickup;
        public float filled;
    }

    public formulaWeights formula_weights;

    void Start()
    {
        /*
         * If there are weights values saved on disk, load them. 
         * Else, use those that have already been obtained from previously carried out trainings.
        */
        if (PlayerPrefs.HasKey("formula_weight_distance"))
        {
            formula_weights.distance = PlayerPrefs.GetFloat("formula_weight_distance");
        }
        else
        {
            formula_weights.distance = 0.4151846f;
        }

        if (PlayerPrefs.HasKey("formula_weight_quantityToPickup"))
        {
            formula_weights.quantityToPickup = PlayerPrefs.GetFloat("formula_weight_quantityToPickup");
        }
        else
        {
            formula_weights.quantityToPickup = 0.1354322f;
        }

        if (PlayerPrefs.HasKey("formula_weight_filled"))
        {
            formula_weights.filled = PlayerPrefs.GetFloat("formula_weight_filled");
        }
        else
        {
            formula_weights.filled = 0.1040449f;
        }

        //Debug.Log("Formula weights: " + formula_weights.distance + ", " + formula_weights.quantityToPickup + ", " + formula_weights.filled);

        getAllShelves();
        initializeShelves();
    }


    float calculateMetric(Robot r, Warehouse_shelf n, Warehouse_node nodo, int quantityToPickup)
    {
        float dist = Vector2.Distance(r.get2dvectortransform(r.transform.position), r.get2dvectortransform(nodo.transform.position));
        float filled = r.containerFilled;

        float m = formula_weights.distance * dist + formula_weights.quantityToPickup * (1/quantityToPickup) + formula_weights.filled * filled;

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
            bestRobotForTask.warehousenodeTarget = nodo;

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
