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
        foreach (Warehouse_shelf n in shelves)
        {
            Warehouse_node nodo = n.node1;
            bool shelf_node_p = true;

            if (Random.Range(0, 100) > 50)
            {
                nodo = n.node2;
                shelf_node_p = false;
            }

            int order_quantity = n.products_to_pick;

            if (order_quantity > 0)
            {
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
                            r.shelf_node_p = shelf_node_p;

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
