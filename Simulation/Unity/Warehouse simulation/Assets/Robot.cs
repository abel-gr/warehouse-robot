using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Robot : MonoBehaviour
{

    Vector3 positionB;
    int robotSpeed = 2;

    Warehouse_node[] nodos;

    void getAllNodes()
    {
        nodos = FindObjectsOfType(typeof(Warehouse_node)) as Warehouse_node[];
        Debug.Log(nodos.Length + " nodos encontrados en el almacen");
    }


    void Start()
    {
        positionB = transform.position;

        getAllNodes();

        ArrayList r = new ArrayList();
        r.Add(2);
        r.Add(5);
        r.Add(1);
        r.Add(8);
        createNewRoute(r);
    }

    Vector2 get2dvectortransform(Vector3 v3)
    {
        Vector2 v;
        v.x = v3.x;
        v.y = v3.z;

        return v;
    }

    void gotoClosestNode()
    {
        float mindist = -1;
        Warehouse_node closestNode = null;

        int i = 0;
        foreach (Warehouse_node node2 in nodos)
        {
            node2.nodeID = i;
            i++;

            float dist = Vector2.Distance(get2dvectortransform(transform.position), get2dvectortransform(node2.transform.position));

            if (closestNode == null || dist < mindist)
            {
                mindist = dist;
                closestNode = node2;
            }
        }

        positionB = closestNode.transform.position;

        Debug.Log("En camino al nodo mas cercano: " + closestNode.transform.position);
    }

    bool wayToClosestNode = false;

    Warehouse_node lastDestination;

    void gotoNode(Warehouse_node node)
    {
        if (lastDestination == null || lastDestination != node)
        {
            if (!wayToClosestNode)
            {
                wayToClosestNode = true;

                gotoClosestNode();
            }
            else
            {
                lastDestination = node;

                positionB = node.transform.position;

                Debug.Log("En camino al nodo ubicado en: " + node.transform.position);
            }
        }
    }

    int lastRoutePositionVisited = -1;

    void goToRoute(ArrayList nodesToVisit)
    {

        if (lastRoutePositionVisited == -1)
        {
            wayToClosestNode = true;
            gotoClosestNode();
        }
        else if(lastRoutePositionVisited < nodesToVisit.Count)
        {
            int i = 0;
            foreach (int n in nodesToVisit)
            {
                if (i >= lastRoutePositionVisited)
                {
                    gotoNode(nodos[n]);
                    Debug.LogWarning("Camino al nodo " + n + " en la posicion de la ruta num " + i);
                    break;
                }
                i++;
            }
        }
    }

    ArrayList nodeRoute;

    void createNewRoute(ArrayList r)
    {
        lastRoutePositionVisited = -1;
        nodeRoute = r;
    }

    void Update()
    {
        if (Vector2.Distance(get2dvectortransform(transform.position), get2dvectortransform(positionB)) <= Time.deltaTime * robotSpeed * 2)
        {
            goToRoute(nodeRoute);
            lastRoutePositionVisited++;
        }
        else
        {
            transform.localPosition = Vector3.MoveTowards(transform.localPosition, positionB, Time.deltaTime * robotSpeed);
        }
    }


    void OnCollisionEnter(Collision collision)
    {
        ContactPoint contact = collision.GetContact(0);
        Quaternion rotation = Quaternion.FromToRotation(Vector3.up, contact.normal);
        Vector3 position = contact.point;
        Collider collider = collision.collider;
    }

}
