using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_box : MonoBehaviour
{
    public bool picked = false;
    public Transform act = null;
    public Rigidbody rig;
    public BoxCollider bc;

    IEnumerator disableGravity()
    {
        yield return new WaitForSeconds(1.5f);

        rig.isKinematic = true;
        rig.useGravity = false;
        bc.enabled = false;
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
