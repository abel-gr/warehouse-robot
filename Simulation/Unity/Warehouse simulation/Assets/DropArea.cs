using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DropArea : MonoBehaviour
{
    void Start()
    {
        
    }

    void Update()
    {
        
    }

    void OnTriggerEnter(Collider collider)
    {
        Robot r = collider.gameObject.GetComponent<Robot>();
        if (r != null)
        {
            Debug.LogError("Robot drop");
        }
    }
}
