using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot_actuator : MonoBehaviour
{

    float p0 = -0.85f;
    float p1 = -1.15f;

    public GameObject boxesContainer;

    public Transform suctionTransform;

    Warehouse_box picked_box = null;

    public void enableActuator()
    {
        transform.localPosition = new Vector3(0, p1, 0);
    }

    public void disableActuator()
    {
        if (picked_box != null)
        {
            picked_box.unpick();

            picked_box.transform.SetParent(boxesContainer.transform);
            //picked_box.transform.localScale = new Vector3(0.3f, 0.1875001f, 0.5f);
        }

        transform.localPosition = new Vector3(0, p0, 0);

        picked_box = null;
    }

    void OnTriggerEnter(Collider collider)
    {
        Warehouse_box r = collider.gameObject.GetComponent<Warehouse_box>();
        if (r != null)
        {
            if (!r.picked)
            {
                if (picked_box == null)
                {
                    picked_box = r;
                    r.act = suctionTransform;
                    r.picked = true;
                }
            }
        }
    }

}
