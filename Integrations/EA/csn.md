
### Before you start, you need to know basics of CAP (Cloud Application Programming) & CSN (Core Schema Notation)

* https://cap.cloud.sap
* https://community.sap.com/t5/human-capital-management-blogs-by-sap/sap-incentive-management-understanding-of-csn-file-amp-cli-command-to/ba-p/13942545



#### List of Types
* https://cap.cloud.sap/docs/cds/types




### Create a CAP Project

```
mkdir <projectname>
cd <projectname>

cds init
```

### Create schema(defination of your custom Model)

```
touch db/schema.cds
```

### Examples ( you can copy and paste it in schema.cds)
```
namespace EXT;

@Common.Label: 'Payments'
@Analytics.query: false
@Analytics.dataCategory: #CUBE
entity payments {

    id: Integer;
    name : String @Common.Label: 'GA13' @Analytics.Dimension @UI.Hidden;
    compdate : Timestamp;

    amount : Decimal @Common.Label: 'Amount' @Analytics.Measure @Aggregation.default: #SUM;
    GENERICNUMBER5 : Decimal @Analytics.Measure @Aggregation.default: #NONE;
}
```



### To Generate CSN Model

```
cds compile db/schema.cds --to csn
```


### Watch and Learn
![Watch to Generate](https://github.com/yogananda-muthaiah/SAP-Sucessfactors-Incentive-Management/blob/main/Integrations/images/2024-11-19_16-35-38.gif)
