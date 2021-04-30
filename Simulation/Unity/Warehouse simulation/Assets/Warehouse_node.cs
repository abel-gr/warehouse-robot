using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_node : MonoBehaviour
{

    public int nodeID = -1;

    public int Edge1 = -1;
    public int Edge2 = -1;
    public int Edge3 = -1;
    public int Edge4 = -1;

    NodesRow nodeRow;

    void Start()
    {
        nodeRow = this.gameObject.GetComponentInParent<NodesRow>();
        if (nodeRow != null)
        {
            Edge2 = nodeRow.RowID;
        }
    }

    void Update()
    {
        
    }
}
