
### Before you start, you need to know basics of CAP (Cloud Application Programming)





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
