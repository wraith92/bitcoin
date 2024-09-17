import React, { useEffect, useState } from "react";
import './App.css';

function App() {
  const [bitcoinData, setBitcoinData] = useState([]);

  // Fonction pour récupérer les messages du backend FastAPI
  const fetchMessages = async () => {
    try {
      const response = await fetch('http://localhost:8000/read_messages/');
      const data = await response.json();
      setBitcoinData(data.messages); // Assurez-vous que la structure JSON correspond à {"messages": [...]}
    } catch (error) {
      console.error("Erreur lors de la récupération des messages:", error);
    }
  };

  useEffect(() => {
    // Appel initial pour récupérer les messages
    fetchMessages();

    // Optionnel : Mettre à jour les données périodiquement toutes les X secondes (ex: 5 secondes)
    const interval = setInterval(() => {
      fetchMessages();
    }, 5000);

    return () => clearInterval(interval); // Nettoyage à la fin
  }, []);

  return (
    <div className="App">
      <h1>Prix du Bitcoin (Temps Réel)</h1>
      <table>
        <thead>
          <tr>
            <th>Timestamp</th>
            <th>Prix d'Achat (Buy Price)</th>
            <th>Prix de Vente (Sell Price)</th>
            <th>Volume</th>
          </tr>
        </thead>
        <tbody>
          {bitcoinData.map((data, index) => (
            <tr key={index}>
              <td>{new Date(data.timestamp * 1000).toLocaleString()}</td>
              <td>{data.buy_price}</td>
              <td>{data.sell_price}</td>
              <td>{data.volume}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
