
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


### To Generate CSN Model

```
cds compile db/schema.cds --to csn
```
