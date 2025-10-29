import React, { useState, useEffect } from "react";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
  } from "../components/ui/select"


 import {handleexchangerequest}  from '../utility/Api'
const ViewBroker = () => {
  const [brokerName, setBrokerName] = useState('IBKR');
  const [apikey, setapikey] = useState("");
  const [secretkey, setsecretkey] = useState("");
  const [AuthToken, setAuthToken] = useState("");
  const [vendorcode, setvendorcode] = useState("");
  const [accountnumber, setaccountnumber] = useState("");
  const [password, setPassword] = useState("");
  const [tableDatafetch, setTableDatafetch] = useState([]);
  const [loading, setLoading] = useState(false);
  const [brokerid, setBrokerid] = useState(false);
  const [REtype, setREType] = useState('POST');
  const [nickname, setnickname] = useState('');




  useEffect(() => {
    // Dummy data for testing
   fetchaccountlist()
  }, []);


  const fetchaccountlist = async () => {
    const type = "GET";
    const endpoint = "loadaccount";
    const payload = "broker=IBKR";
    setLoading(true); // Set loading to true before fetching data
    handleexchangerequest(type, payload, endpoint, false)
      .then((response) => {
        console.log(response);
        setTableDatafetch(response || []); // Ensure response is an array
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
      })
      .finally(() => {
        setLoading(false); // Set loading to false after fetching data
      });
  };

  


    

  

  const handleAddBroker = () => {
    let put= false
    if (REtype=="PUT"){
      put = true
    }
    const payload = JSON.stringify({
      brokerName,
      apikey,
      secretkey,
      AuthToken,
      vendorcode,
      accountnumber,
      password,
      put,
      brokerid,
      nickname

    });
    
      const Rtype = REtype
        const endpoint= "broker"
        handleexchangerequest(Rtype, payload, endpoint,true)
    .then(response => {
    console.log(response) 
    setREType('POST')
    setBrokerid(false)

    
    window.location.reload()
    })
  






  
 
    // Add API call logic here to save the broker details
  };
const handlelogin = async (brokerid) => {
        const payload = JSON.stringify({brokerid });
        const type = "POST"
        const endpoint= "loginbroker"
        handleexchangerequest(type, payload, endpoint,true)
    .then(response => {
    console.log(response) 
    setBrokerid(false)

    
    window.location.reload()
    })
  }


  const handleadelete=(brokerid)=>{
  
       const payload = 'brokerid='+brokerid;
          const type = "DELETE"
          const endpoint= "broker"
          handleexchangerequest(type, payload, endpoint,true)
      .then(response => {
      console.log(response) 
      setBrokerid(false)
      
      window.location.reload()
      })
  
    }
  

   
  
  const handleactivebroker=(brokerid)=>{
    const put= false;
     const payload = JSON.stringify({brokerid, put});
        const type = "PUT"
        const endpoint= "broker"
        handleexchangerequest(type, payload, endpoint,true)
    .then(response => {
    console.log(response) 
    setBrokerid(false)

    
    window.location.reload()
    })

  }

  const handleEdit = (brokerid) => {
    const rowData = tableDatafetch[brokerid];
    console.log(rowData,'rowdata')
    setBrokerName(rowData.brokername);
    setapikey(rowData.apikey);
    setsecretkey(rowData.secretkey);
    setAuthToken(rowData.AuthToken);
    setvendorcode(rowData.vendorcode);
    setaccountnumber(rowData.accountnumber);
    setPassword(rowData.password);
    setBrokerid(rowData.brokerid)
    setREType('PUT')
  };


  return (
    <div className="container mx-auto p-6 bg-gray-100 rounded-lg shadow-md max-w-7xl">
      <h1 className="text-2xl font-bold text-blue-800 mb-6">Add Broker</h1>
      <form className="flex flex-col gap-4">
        <div className="flex items-center gap-4">
          <Label htmlFor="broker-name" className="w-1/3 text-lg text-gray-700">
            Broker Name
          </Label>
          <Input
            id="broker-name"
            type="text"
            value={brokerName}
            readOnly
            className="w-2/3 p-2 border border-gray-300 rounded-md bg-gray-200 pointer-events-none"
          />
        </div>
        <div className="flex items-center gap-4">
          <Label htmlFor="broker-name" className="w-1/3 text-lg text-gray-700">
            Nick Name
          </Label>
          <Input
            id="broker-name"
            type="text"
            placeholder="Enter Nick Name"
            value={nickname}
            onChange={(e) => setnickname(e.target.value)}
            className="w-2/3 p-2 border border-gray-300 rounded-md"
          />
        </div>
        {/* Other input fields */}
        <div className="flex items-center gap-4">
          <Label htmlFor="api-key" className="w-1/3 text-lg text-gray-700">
            API Key
          </Label>
          <Input
            id="api-key"
            type="text"
            placeholder="Enter API key"
            value={apikey}
            onChange={(e) => setapikey(e.target.value)}
            className="w-2/3 p-2 border border-gray-300 rounded-md"
          />
        </div>
        {/* Auth Token */}
        <div className="flex items-center gap-4">
          <Label htmlFor="auth-token" className="w-1/3 text-lg text-gray-700">
            Auth Token
          </Label>
          <Input
            id="auth-token"
            type="text"
            placeholder="Enter Auth Token"
            value={AuthToken}
            onChange={(e) => setAuthToken(e.target.value)}
            className="w-2/3 p-2 border border-gray-300 rounded-md"
          />
        </div>

        {/* Vendor Code */}
        <div className="flex items-center gap-4">
          <Label htmlFor="vendor-code" className="w-1/3 text-lg text-gray-700">
            Vendor Code
          </Label>
          <Input
            id="vendor-code"
            type="text"
            placeholder="Enter Vendor Code"
            value={vendorcode}
            onChange={(e) => setvendorcode(e.target.value)}
            className="w-2/3 p-2 border border-gray-300 rounded-md"
          />
        </div>

        {/* Account Number */}
        <div className="flex items-center gap-4">
          <Label htmlFor="account-number" className="w-1/3 text-lg text-gray-700">
            Account Number
          </Label>
          <Input
            id="account-number"
            type="text"
            placeholder="Enter Account Number"
            value={accountnumber}
            onChange={(e) => setaccountnumber(e.target.value)}
            className="w-2/3 p-2 border border-gray-300 rounded-md"
          />
        </div>

        {/* Password */}
        <div className="flex items-center gap-4">
          <Label htmlFor="password" className="w-1/3 text-lg text-gray-700">
            Password
          </Label>
          <Input
            id="password" 
            type="password"
            placeholder="Enter Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-2/3 p-2 border border-gray-300 rounded-md"
          />
        </div>

        {/* Submit Button */}
        <div className="flex justify-end">
          <Button
            type="button"
            onClick={()=>handleAddBroker()}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Broker
          </Button>
        </div>
      </form>

      <div className="container mx-auto mt-6 p-6 bg-gray-100 rounded-lg shadow-md max-w-6xl">
        <div className="overflow-x-auto">
          {loading ? (
            <p className="text-center text-gray-700">Loading...</p>
          ) : tableDatafetch.length === 0 ? (
            <p className="text-center text-gray-700">No data available</p>
          ) : (
            <table className="min-w-full table-auto">
              <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
                <tr>            
                                <th className="px-6 py-3">Status</th>

                                {Object.keys(tableDatafetch[0])
                                  .filter((key) => key !== 'status' && key !== 'active')
                                  .map((key) => (
                                    <th key={key} className="px-6 py-3">
                                      {key.charAt(0).toUpperCase() + key.slice(1)}
                                    </th>
                                  ))}
                                
                                <th className="px-6 py-3">Active</th>
                                <th className="px-6 py-3">Login</th>
                                <th className="px-6 py-3">Edit</th>
                                <th className="px-6 py-3">Delete</th>
                              </tr>
              </thead>
              <tbody>
                
                {tableDatafetch.map((row, index) => (
                  <tr
                    key={index}
                    className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                  >

                        {Object.entries(row)
                        
      .filter(([key]) => key !== 'valid' && key !== 'active')
      .map(([key, value], idx) => (
        
        <td key={idx} className="px-6 py-4">
          {value}
        </td>
      ))}               
                <td className={row.status?"bg-green-600 text-white py-2 text-sm rounded-md hover:bg-blue-700":"bg-red-600 text-white py-2 text-sm rounded-md hover:bg-blue-700"}> 
                  {row.status?"CONNECTED":"DISCONNECTED"}

                  </td>

{/* 
                    <td className="px-6 py-4 text-center">
                      <Button
                        className="bg-blue-600 text-white py-2 text-sm rounded-md hover:bg-blue-700"
                        onClick={() => handleactivebroker(row.brokerid)}
                      >
                        {row.active?"Deactivate":"Activate"}
                      </Button>
                    </td> */}
                   
                    <td className="px-6 py-4 text-center">
                         <Button
                        className={row.valid?"bg-green-600 text-white py-2 text-sm rounded-md hover:bg-blue-700":"bg-red-600 text-white py-2 text-sm rounded-md hover:bg-blue-700"}
                        onClick={() => handlelogin(row.brokerid)}
                      >
                        Login
                      </Button>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Button
                        className="bg-blue-600 text-white py-2 text-sm rounded-md hover:bg-blue-700"
                        onClick={() => handleEdit(index)}
                      >
                        Edit
                      </Button>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Button
                        className="bg-blue-600 text-white py-2 text-sm rounded-md hover:bg-blue-700"
                        onClick={() => handleadelete(row.brokerid)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default ViewBroker;