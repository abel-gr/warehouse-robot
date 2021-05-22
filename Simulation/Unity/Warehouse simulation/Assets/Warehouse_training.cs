using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Warehouse_training : MonoBehaviour
{
    public Warehouse warehouse;
    public Warehouse_orders warehouse_Orders;

    public static bool trainingMode = false;

    public static int robotsFinished = 0;

    public Warehouse_orders.formulaWeights bestWeights;
    public float minLoss = -1;

    void Start()
    {
        if (trainingMode)
        {
            if (PlayerPrefs.HasKey("formula_weight_loss"))
            {
                minLoss = PlayerPrefs.GetFloat("formula_weight_loss");
            }
        }
        
    }

    float iteration_start_time = 0;
    float iteration_elapsed_time = 0;

    float variable_learning_rate;

    private void newWeights()
    {
        variable_learning_rate = Random.Range(-10.0f, 10.0f);
        warehouse_Orders.formula_weights.distance -= variable_learning_rate * (1 / iteration_elapsed_time);

        variable_learning_rate = Random.Range(-10.0f, 10.0f);
        warehouse_Orders.formula_weights.quantityToPickup -= variable_learning_rate * (1 / iteration_elapsed_time);

        variable_learning_rate = Random.Range(-10.0f, 10.0f);
        warehouse_Orders.formula_weights.filled -= variable_learning_rate * (1 / iteration_elapsed_time);

        //Debug.Log("New weights: " + warehouse_Orders.formula_weights.distance + ", " + warehouse_Orders.formula_weights.quantityToPickup + ", " + warehouse_Orders.formula_weights.filled);
    }

    public bool firstIteration = true;

    public void startTrainingIteration()
    {
        Debug.Log("startTrainingIteration");

        if (firstIteration)
        {
            firstIteration = false;
        }
        else
        {
            newWeights();
        }

        iteration_start_time = Time.time;

        foreach (Warehouse_shelf r in warehouse_Orders.shelves)
        {
            if(Random.Range(0.0f, 1.0f) > 0.6f)
            {
                r.products_to_pick = 1;
            }
        }
    }

    int ordersPerIteration = 10;

    void Update()
    {
        if (trainingMode)
        {
            if (robotsFinished >= ordersPerIteration)
            {
                robotsFinished = 0;

                iteration_elapsed_time = Time.time - iteration_start_time;

                float cLoss = iteration_elapsed_time;

                if (cLoss < minLoss || minLoss <= 0)
                {
                    minLoss = cLoss;
                    bestWeights = warehouse_Orders.formula_weights;

                    PlayerPrefs.SetFloat("formula_weight_loss", cLoss);

                    PlayerPrefs.SetFloat("formula_weight_distance", bestWeights.distance);
                    PlayerPrefs.SetFloat("formula_weight_quantityToPickup", bestWeights.quantityToPickup);
                    PlayerPrefs.SetFloat("formula_weight_filled", bestWeights.filled);
                }

                Debug.Log("Iteration elapsed time in seconds: " + iteration_elapsed_time);

                startTrainingIteration();
            }
        }
    }
}
