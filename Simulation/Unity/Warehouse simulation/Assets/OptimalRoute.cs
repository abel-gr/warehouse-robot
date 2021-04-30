using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class OptimalRoute : MonoBehaviour
{
    public Robot robot;

    void Start()
    {

    }

    float minimaDistanciaTotal = -1;
    public List<Warehouse_node> bestRoute = new List<Warehouse_node>();

    void routeRec(Warehouse_node n1, Warehouse_node n2, List<Warehouse_node> routeR, float distanciaActual)
    {
        foreach (Warehouse_node n3 in robot.warehouse.nodos)
        {
            if (n3 != n1 && routeR.Count < 5)
            {
                if (bestRoute.Count == 0 || distanciaActual <= minimaDistanciaTotal) {

                    if ((n1.Edge1 == n3.Edge1 && n1.Edge1 != -1) || (n1.Edge2 == n3.Edge2 && n1.Edge2 != -1))
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

    public ArrayList calculateOptimalRoute(Warehouse_node n1, Warehouse_node n2)
    {
        Debug.LogWarning("Begin route from " + n1.nodeID + " to " + n2.nodeID);

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
