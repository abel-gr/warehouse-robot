using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_shelf : MonoBehaviour
{
    public int id = -1;

    public int products = 2;
    public int products_to_pick = 0;

    public Warehouse_node node1;
    public Warehouse_node node2;

    public Warehouse_orders warehouse_orders;

    public Warehouse_box[] boxes;

    void Start()
    {
        initializeShelf();
    }

    public IEnumerator generateOrder()
    {
        int tiempo = Random.Range(0, 10);
        yield return new WaitForSeconds(tiempo);

        if(Random.Range(0, 100) > 80)
        {

            products_to_pick++;

            Debug.Log("New order generated in node " + node1.nodeID);
        }

    }

    void initializeShelf()
    {
        warehouse_orders = FindObjectOfType(typeof(Warehouse_orders)) as Warehouse_orders;
    }

    bool generateOrderB = true;

    void Update()
    {
        if (generateOrderB)
        {
            generateOrderB = false;
            StartCoroutine(generateOrder());
        }
    }
}
