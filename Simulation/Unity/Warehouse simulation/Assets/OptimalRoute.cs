using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OptimalRoute : MonoBehaviour
{
    public Robot robot;

    void Start()
    {

    }

    /* Each node has a direction of X and a direction of Z depending on the
     * row and column where it is located, to have lane directions on the warehouse
     * and avoid frontal collisions between robots.
     */
    bool nodeDirection(Warehouse_node n1, Warehouse_node n3)
    {
        bool r = false;

        if(n1.Edge1 == n3.Edge1)
        {
            int z1 = (int) n1.transform.position.z;
            int z3 = (int) n3.transform.position.z;

            if (!n1.directionZ && z3 <= z1)
            {
                r = true;
            }
            else if (n1.directionZ && z3 >= z1)
            {
                r = true;
            }
        }
        else if (n1.Edge2 == n3.Edge2)
        {
            int x1 = (int) n1.transform.position.x;
            int x3 = (int) n3.transform.position.x;

            if (n1.directionX && x3 >= x1)
            {
                r = true;
            }
            else if (!n1.directionX && x3 <= x1)
            {
                r = true;
            }
        }


        return r;
    }

    float minimaDistanciaTotal = -1;
    public List<Warehouse_node> bestRoute = new List<Warehouse_node>();

    void routeRec(Warehouse_node n1, Warehouse_node n2, List<Warehouse_node> routeR, float distanciaActual)
    {
        foreach (Warehouse_node n3 in robot.warehouse.nodos)
        {
            if (n3 != n1 && routeR.Count < 6)
            {
                if (bestRoute.Count == 0 || distanciaActual <= minimaDistanciaTotal) {

                    if ((n1.Edge1 == n3.Edge1 && n1.Edge1 != -1) || (n1.Edge2 == n3.Edge2 && n1.Edge2 != -1))
                    {
                        if (nodeDirection(n1, n3))
                        {

                            if (!routeR.Contains(n3))
                            {
                                List<Warehouse_node> newRoute = new List<Warehouse_node>(routeR);
                                newRoute.Add(n3);

                                float newDistance = distanciaActual + Vector2.Distance(robot.get2dvectortransform(n1.transform.position), robot.get2dvectortransform(n3.transform.position));

                                if (n3 == n2)
                                {
                                    if (bestRoute.Count == 0 || newDistance < minimaDistanciaTotal)
                                    {
                                        minimaDistanciaTotal = newDistance;
                                        bestRoute = newRoute;
                                    }

                                }
                                else
                                {
                                    routeRec(n3, n2, newRoute, newDistance);
                                }
                            }

                        }
                    }
                }
            }
        }
    }

    public ArrayList calculateOptimalRoute(Warehouse_node n1, Warehouse_node n2)
    {
        Debug.LogWarning("Begin route from " + n1.nodeID + " to " + n2.nodeID);

        bestRoute = new List<Warehouse_node>();

        List<Warehouse_node> route = new List<Warehouse_node>();
        route.Add(n1);
        routeRec(n1, n2, route, 0);

        ArrayList rutaIDs = new ArrayList();
        foreach (Warehouse_node n3 in bestRoute)
        {
            rutaIDs.Add(n3.nodeID);
            //Debug.LogWarning("Route node: " + n3.nodeID);
        }

        //Debug.Log("Min distance: " + minimaDistanciaTotal);

        return rutaIDs;
    }
}
