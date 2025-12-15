# End-to-End E-Commerce Logistics Analysis (Python & Power BI)
This project analyzes delivery performance for 50,000 e-commerce orders.
The workflow includes data cleaning and KPI engineering in Python, followed by
an interactive Power BI dashboard to evaluate on-time delivery, delivery speed,
and regional delay patterns.

## Technical Approach

The project follows an end-to-end analytics workflow, starting from raw data ingestion to business-ready visualization.

### Data Processing (Python)

All data preparation is handled in `src/analysis.py` using Python and Pandas:

1. **Data Loading**
   - Reads the raw E-Commerce Order Fulfillment dataset (50K records).
   - Standardizes column names for consistency.

2. **Date Cleaning & Engineering**
   - Parses `order_date`, `ship_date`, and `delivery_date`.
   - Implements a realistic domestic e-commerce dispatch model:
     - Same-day shipping for short delivery cycles.
     - Next-day or 3-day dispatch for longer delivery cycles.
   - Recalculates delivery duration (`delivery_days`) to ensure timeline consistency.

3. **KPI Engineering**
   - On-time delivery flag based on delivery status.
   - Delay flag for late deliveries.
   - Aggregated metrics such as average delivery days and on-time delivery rate.

4. **Data Export**
   - Outputs a clean, analysis-ready dataset (`cleaned_merged_data.csv`) used directly in Power BI.
   - Generates static charts (PNG) for exploratory analysis and documentation.

This separation ensures that all business logic is reproducible in code, while Power BI focuses purely on visualization.


## Power BI Dashboard

The dashboard was built using Power BI (online) and visualizes the cleaned dataset
produced by the Python analysis pipeline.

**Key insights:**
- On-time delivery rate and average delivery days (KPI cards)
- Monthly order volume trend
- Delivery delays by customer region
- Interactive filtering by region, shipping mode, and product category

### Dashboard Overview
![Dashboard Overview](end-to-end-delivery-ecommerce-logistics-analysis/assets/dashboard_overview.png)

## Business Insight


Based on the analysis of 50,000 e-commerce orders, several operational insights emerge:

- **On-Time Delivery Performance**
  - Approximately 85% of orders are delivered on time.
  - While overall performance is strong, there is room for improvement in specific regions and shipping modes.

- **Delivery Speed**
  - The average delivery time is approximately 6–7 days.
  - Faster shipping modes consistently show better on-time performance.

- **Regional Delays**
  - Certain customer regions experience a higher number of delivery delays.
  - This may indicate capacity constraints, last-mile challenges, or suboptimal warehouse allocation.

- **Demand Patterns**
  - Monthly order volume shows clear fluctuations over time.
  - Understanding these trends can help with capacity planning and lead the marketing strategies as well.

## Recommendations

The analysis highlights several opportunities to improve both delivery operations and customer experience.
Refine shipping choices: Shipping options with higher delay rates should be reviewed. For urgent or high-value orders, prioritizing faster delivery methods can help reduce late deliveries and improve reliability.
Focus on high-delay regions: Some regions experience more frequent delays, suggesting potential last-mile or capacity issues. Targeted logistics improvements in these areas could lead to noticeable performance gains.
Plan using demand patterns: Order volumes fluctuate over time. Using these trends for inventory and workforce planning can help maintain delivery performance during busy periods.
Use delivery performance in marketing: Regions and shipping options with strong on-time performance can be promoted as a reliability advantage. Promotions can also be timed during lower-demand periods to balance workload and improve service quality.
Next steps: Future work could include factoring in product value when selecting shipping methods and using predictive models to flag orders that are likely to be delayed.





