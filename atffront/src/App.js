import bottle from './assets/bottle.png';
import './App.css';
import ProductForm from './components/ProductForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <div className="flex items-center flex-direction row justify-center space-x-4">
          <p className="text-5xl text-amber-200 font-bold">ATF</p>
          <div>
            <div>
              <img src={bottle} className="App-bottle" alt="bottle" />
            </div>
          </div>
          <p className="text-5xl text-amber-200 font-bold">Scanner</p>
        </div>
        
        

      </header>
      <main>
        
          <h2 className="text-2xl font-semibold mb-4 text-center text-white">
            Alcoholic Beverage Product Registration
          </h2>
          <div className="h-4"><ProductForm /></div>
      </main>
    </div>
  );
}

export default App;
