using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_box : MonoBehaviour
{
    public bool picked = false;
    public Transform act = null;
    public Rigidbody rig;
    public BoxCollider bc;
    public Transform bshelf;

    IEnumerator disableGravity()
    {
        yield return new WaitForSeconds(2.0f);

        rig.isKinematic = true;
        rig.useGravity = false;
        bc.enabled = false;
    }

    public void enableGravity()
    {
        rig.isKinematic = false;
        rig.useGravity = true;
        bc.enabled = true;

        if (bshelf != null)
        {
            transform.SetParent(bshelf);
        }
    }

    public void unpick()
    {
        picked = false;
        rig.isKinematic = false;
        rig.useGravity = true;

        StartCoroutine(disableGravity());
    }

    void Update()
    {
        if (picked && act != null)
        {
            transform.position = act.transform.position;
        }        
    }

}
