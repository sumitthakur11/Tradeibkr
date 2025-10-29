import React from 'react'
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "../components/ui/select"

import { Button } from "../components/ui/button";
import { useState,useEffect } from 'react';
import { handleexchangerequest } from '../utility/Api';
import PropTypes from 'prop-types';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Box from '@mui/material/Box';
import { DataGrid, GridColumnHeaderSeparatorSides } from '@mui/x-data-grid';
import Paper from '@mui/material/Paper';
import { Flex } from '@mantine/core';
import { columnGroupsStateInitializer } from '@mui/x-data-grid/internals';
import { useNavigate } from 'react-router-dom';
import { RefreshCcw } from 'lucide-react';
import { DownloadCSVFromJSON } from '../utility/downloadcsv';



function CustomTabPanel(props) {
  const { children, value, index, ...other } = props;
  

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

CustomTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.number.isRequired,
  value: PropTypes.number.isRequired,
};
function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const OrderStatus = () => {
      const [loading,setLoading]= useState('')
      const [tableDatafetch, setTableDatafetch] = useState([]);
    const [brokerName4, setBrokerName4] = React.useState(null);
    const [exchange, setExchange] = React.useState(null);
    const [value, setValue] = React.useState(0);
    const [tableDatafetch2, setTableDatafetch2] = useState([]);
    const [tableDatafetch3, setTableDatafetch3] = useState([]);
    const[filtereddata,setfiltereddata]= useState([])
    const[selectedorder,setselectedorder]= useState([])
    const[openfil,setopenfil]= useState('')
    const [canceldata,setcanceldata]= useState([])
    


    const [selectedRows, setSelectedRows] = useState([]);

    const navigate  = useNavigate();

  const handleChange = (event, newValue) => {
    setValue(newValue);
  }


const paginationModel = { page: 0, pageSize: 10 };



  const fetchTableData = async (t,setdata) => {
    setLoading(true);
    try {
      const type = "GET";
      const endpoint = "position"; // Replace with your API endpoint
      const payload = "type="+t; // Example payload
      const response = await handleexchangerequest(type, payload, endpoint, false);
      if (response) {
        setdata(response);
        console.log(response,'response')
      } else {
        console.error("Failed to fetch table data");
      }
    } catch (error) {
      console.error("Error fetching table data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTableData('all',setTableDatafetch);


  }, []);


  useEffect(()=>{
  const dataWithIds = tableDatafetch.map((item, index) => ({
    ...item,
    id: item.id, // Add a unique id based on the index
  }));
  setfiltereddata(dataWithIds);
  console.log(dataWithIds, 'filteredAndSortedProjects');
}, [tableDatafetch])
    


const handleOrderselect=(value)=>{

console.log(value.ids,'valuesss')
setselectedorder(value.ids)
const idsArray = Array.from(value.ids); // Convert Set to Array
const updatedData = filtereddata.filter((row) => idsArray.includes(row.orderid));
console.log(updatedData)
setcanceldata(updatedData)




}


const handlecancelorder = ()=>{
    
        const obj= JSON.stringify(canceldata)
        
        const payload ="selectedRows="+obj
        const type = "GET"
        const endpoint= "placeorder"
        handleexchangerequest(type, payload, endpoint,true)
    .then(response => {
    console.log(response) 
    
    })
    

  




}
  const handleSelectIndex = (value) => {
      if (value) {

    const fill = tableDatafetch.filter((item) =>
    item.orderstatus.toLowerCase().includes(value.toLowerCase())
  );
      console.log(fill,value.toLowerCase())

      setfiltereddata(fill)

     


    }

    };
    const handleDelete = () => {
  // Ensure selectedRows is an array
  
  const selectedIds = Array.isArray(selectedRows) ? selectedRows : Array.from(selectedRows);
  console.log(selectedIds, 'selectedIds');
  // Filter out the selected rows
  const updatedData = filtereddata.filter((row) => !selectedIds.includes(row.id));

  // Update the state
  setfiltereddata(updatedData);
  setSelectedRows([]); // Clear the selection
};

const handleModify = (row) => {

  navigate('/OrderPunch', { state: { data: row , action: row.transactiontype,modify:true} });
};


    
  //     const handleSelectIndex = (value) => {
  //        if (value === "Complete") {
  //     // fetchSymbols(brokerName4, value)
  //       setExchange(value)


  //   }
  // }
  return (
    <>
     <Box sx={{ width: '100%' }}>

      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <RefreshCcw className="cursor-pointer" onClick={fetchTableData} >
        </RefreshCcw>
     
        <p>Refresh</p>

        <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
          <Tab label="Order Book" className='text-slate-900 font-bold' {...a11yProps(0)} />
          {/* <Tab label="Open Position"className='text-slate-900 font-bold' {...a11yProps(1)} />
          <Tab label="Close Position"className='text-slate-900 font-bold' {...a11yProps(2)} /> */}
        </Tabs>
      </Box>
      

      <CustomTabPanel value={value} index={0}>
        <span>Order Book</span>
        
        
        {/* Render the Select component only when the "Order Book" tab is selected */}
        <div className='flex flex-wrap items-center justify-around gap-4'>
              <Button color="primary" className="p-3 bg-cyan-700/85" onClick = {() => DownloadCSVFromJSON(filtereddata,"orderbook.csv")}>
                  Download
                </Button>
        
          {value === 0 && (
            <Select onValueChange={(value) => {handleSelectIndex(value),setopenfil(value)}}>
              
              <SelectTrigger className="w-40 max-xs:w-20 bg-sky-700/85 text-white hover:bg-sky-700">
                <SelectValue placeholder="Select Status" />
              </SelectTrigger>
              <SelectContent className="bg-white border border-blue-300">
                <SelectItem
                  value="Complete"
                  className="hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200"
                >
                  Completed
                </SelectItem>
                <SelectItem
                  value="Rejected"
                  className="hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200"
                >
                  Rejected
                </SelectItem>
                <SelectItem
                  value="Open"
                  className="hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200"
                >
                  Open
                </SelectItem>
                <SelectItem
                  value="Cancelled"
                  className="hover:bg-blue-100 hover:text-blue-800 focus:bg-blue-200"
                >
                  Cancelled
                </SelectItem>
              </SelectContent>
            </Select>
          )}
          
          
          <div className='container flex items-end gap-2 flex-col  mx-auto mt-6 p-6 bg-trasparent rounded-lg max-w-6xl'>

            <Button onClick={()=>handlecancelorder()} className=" bg-red-600/95">Cancel </Button>
            
             <Paper sx={{ height: '100%', width: '100%' }}>
              
  <DataGrid
    className='text-black overflow-x-scroll scrollbar-hide'
    rows={filtereddata} // Use filtereddata as rows
    getRowId={(row) => row.orderid} // Ensure this matches the unique identifier
    disableSelectionOnClick
    
    columns={[
      {
      field: 'Modify',
      headerName: 'Modify',
      width:150,
      renderCell: (params) =>(
    
        <Button   color="primary" className="p-3 bg-teal-700/85" onClick={() => handleModify(params.row)}>
          Modify
        </Button>
      )
    } ,
      ...Object.keys(filtereddata[0] || {}).map((key) => (
      {
      field: key,
      headerName: key.charAt(0).toUpperCase() + key.slice(1),
      // flex: 1, // Adjust column width
      width:150
    })),
    
    
    
    
    
    
    
    
    
    
    ]}
    initialState={{ pagination: { paginationModel } }}
    pageSizeOptions={[10, 20,50]} // Enable page size options
    checkboxSelection
    onRowSelectionModelChange={(value)=>{handleOrderselect(value),setSelectedRows(value.id)}}
    sx={{ border: 0 , '.MuiDataGrid-columnHeaderTitle': { fontWeight: 'bold' }}}     />
</Paper>
         
</div>
        </div>
      </CustomTabPanel>
      
    </Box>
    </>
  )
}

export default OrderStatus