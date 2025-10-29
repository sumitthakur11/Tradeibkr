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
  import { LuDownload } from "react-icons/lu";
import { MdDeleteForever } from "react-icons/md";
import { MdModeEdit } from "react-icons/md";
 import {handleexchangerequest}  from '../utility/Api'
import { Type } from "lucide-react";
import { Host_Ip } from "../utility/Host";
const Angel = () => {
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
    const [nickname, setnickname] = useState('');

      const [REType, setREType] = useState('POST');


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
     if (REType=="PUT"){
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
    
      const Rtype = REType
        const endpoint= "broker"
        handleexchangerequest(Rtype, payload, endpoint,true)
    .then(response => {
    console.log(response) 
    
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
    const put = false
     const payload = JSON.stringify({brokerid,put });
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


  const handleDownloadLog = async (brokerid) => {
    try {
        const sdd = localStorage.getItem("token");
        const csrf = localStorage.getItem("csrf");
      const t = "token " + sdd;

      const payload = JSON.stringify({ brokerid });
      const type = "POST";
      const endpoint = "v1/ibkr/downloadlog"; 

      
      const response = await fetch(Host_Ip+ endpoint, {
              method: type,
              headers: {
                "Content-Type": "application/json",
                'X-CSRFToken':csrf,
      
                Authorization: t,
              },
              body: payload,
            });
            if (!response.ok) {
              alert('something went wrong hii 2')
      
              throw new Error("Login failed");
            }
      if (!response.ok) {
        throw new Error('Failed to download log file');
      }

      const content = response.headers.get('Content-Disposition');
      let filename = `broker_${brokerid}.log`;
      if (content) {
        const filenameMatch = content.match(/filename="(.+)"/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      } catch (error) 
      {
      console.error("Error downloading log file:", error);
      alert("Failed to download log file");
    }
  }


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
        {/* Other input fields */}

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
        {/* <div className="flex items-center gap-4">
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
        </div> */}

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

                 {Object.keys(tableDatafetch[0])
                                  .filter((key) => key !== 'valid' && key !== 'active')
                                  .map((key) => (
                                    <th key={key} className="px-6 py-3">
                                      {key.charAt(0).toUpperCase() + key.slice(1)}
                                    </th>
                                  ))}
                  <th   className="px-6 py-3"> Active</th>
                  <th className="px-6 py-3">Edit</th>
                  <th className="px-6 py-3">Delete</th>
                  <th className="px-6 py-3">Download</th>
                </tr>
              </thead>
              <tbody>
                {tableDatafetch.map((row, index) => (
                  <tr
                    key={index}
                    className="bg-white border-b dark:bg-gray-800 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600"
                  >
                    
                    
                      <td className={row.status?" text-green-600  ":"text-red-600 "}> 
                  {row.status?"Connected":"Disconnected"}

                  </td>
                        {Object.entries(row)
      .filter(([key]) => key !== 'status' && key !== 'active')
      .map(([key, value], idx) => (
        <td key={idx} className="px-6 py-4">
          {value}
        </td>

      ))}

                    <td className="px-6 py-4 text-center">
                      <Button
                        className={`bg-blue-600 text-white py-2 text-sm rounded-md hover:bg-blue-700 ${row.active ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}`}
                        onClick={() => handleactivebroker(row.brokerid)}
                      >
                        {row.active?"Deactivate":"Activate"}
                      </Button>
                    </td>
                  
                    <td className="px-6 py-4 text-center">
                      <Button
                        className="bg-blue-600 text-white py-2 text-sm rounded-md hover:bg-blue-700"
                        onClick={() => handleEdit(index)}
                      >
                        Edit <MdModeEdit />

                      </Button>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Button
                        className="bg-red-600/95 text-white py-2 text-sm rounded-md hover:bg-red-700"
                        onClick={() => handleadelete(row.brokerid)}
                      >
                        Delete <MdDeleteForever />
                      </Button>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <Button
                        className="bg-green-600 text-white py-2 text-sm rounded-md hover:bg-green-700"
                        onClick={() => handleDownloadLog (row.brokerid)}
                      >
                        Download <LuDownload />
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

export default Angel;