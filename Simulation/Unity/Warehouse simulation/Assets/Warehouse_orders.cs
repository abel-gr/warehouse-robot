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

    void assignRobot()
    {
        foreach (OrderInfo n in globalOrders)
        {
            Warehouse_node nodo = n.node;
            int order_quantity = n.quantity;

            if (order_quantity > 0)
            {
                foreach (Robot r in warehouse.robots)
                {
                    if (r.RobotState == Robot.RobotStates.Available)
                    {
                        order_quantity = n.quantity;
                        if (order_quantity > 0)
                        {
                            int canPickup = r.containerCapacity - r.containerFilled;

                            int quantityToPickup = 0;

                            if (order_quantity > canPickup)
                            {
                                quantityToPickup = canPickup;
                                n.quantity = order_quantity - canPickup;
                            }
                            else if (order_quantity == canPickup)
                            {
                                quantityToPickup = canPickup;
                                n.quantity = 0;
                            }
                            else
                            {
                                quantityToPickup = order_quantity;
                                n.quantity = 0;
                            }

                            r.containerFilled += quantityToPickup;

                            warehouse.setRobotRoute(r.robotID, -1, nodo.nodeID);
                            r.RobotState = Robot.RobotStates.OnWayToPick;

                        }
                    }
                }
            }
        }

    }

    public void addOrder(Warehouse_node node, int quantity)
    {
        OrderInfo kv = new OrderInfo(node, quantity);
        globalOrders.Add(kv);
    }

    void Start()
    {
        getAllShelves();
        initializeShelves();
    }

    void Update()
    {
        if (robotsReady)
        {
            assignRobot();
        }
    }
}
