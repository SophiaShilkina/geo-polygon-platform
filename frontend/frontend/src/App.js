import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Marker } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const WS_URL = 'ws://localhost:8000/ws/polygons/';

const App = () => {
    const [name, setName] = useState('');
    const [coordinates, setCoordinates] = useState([]);
    const [polygons, setPolygons] = useState([]);
    const [invalidPolygons, setInvalidPolygons] = useState([]);
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        const ws = new WebSocket(WS_URL);
        ws.onopen = () => console.log("Connected to WebSocket");
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.status === "invalid") {
                setInvalidPolygons(prev => [...prev, data]);
                alert(`Ошибка: Полигон ${data.polygon.name} пересекается с другими`);
            }
        };
        ws.onclose = () => console.log("WebSocket disconnected");
        setSocket(ws);

        return () => {
            ws.close();
        };
    }, []);

    const addPoint = (lat, lng) => {
        setCoordinates([...coordinates, [lat, lng]]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await axios.post('http://localhost:8000/api/polygons/', {
                name,
                coordinates,
            });
            setPolygons([...polygons, response.data]);
            setCoordinates([]);
            setName('');
        } catch (error) {
            console.error('Error submitting polygon:', error);
        }
    };

    const loadPolygons = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/polygons/');
            setPolygons(response.data);
        } catch (error) {
            console.error('Error loading polygons:', error);
        }
    };

    useEffect(() => {
        loadPolygons();
    }, []);

    return (
        <div className="container">
            <h1>Добавление полигона</h1>
            <form onSubmit={handleSubmit}>
                <div className="form-group">
                    <label htmlFor="name">Название полигона:</label>
                    <input
                        type="text"
                        id="name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="coordinates">Координаты:</label>
                    <textarea id="coordinates" value={JSON.stringify(coordinates)} readOnly rows="4" />
                </div>
                <div className="form-group">
                    <button type="button" onClick={() => addPoint(prompt('Введите широту:'),
                        prompt('Введите долготу:'))}>
                        Добавить точку
                    </button>
                </div>
                <button type="submit">Сохранить</button>
            </form>

            <h2>Сохраненные полигоны</h2>
            <MapContainer center={[55.75, 37.61]} zoom={5} style={{ height: '400px', width: '100%' }}>
                <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                           attribution='© OpenStreetMap contributors' />
                {coordinates.map((point, index) => <Marker key={index} position={point} />)}
                {polygons.map((polygon, index) => <Polygon key={index} positions={polygon.coordinates} />)}
                {invalidPolygons.map((polygon, index) => <Polygon key={index}
                                                                  positions={polygon.polygon.coordinates}
                                                                  color="red" />)}
            </MapContainer>

            <h2>Ошибки</h2>
            <ul>
                {invalidPolygons.map((poly, index) => (
                    <li key={index}>
                        Полигон <strong>{poly.polygon.name}</strong>
                        пересекается с {poly.intersecting_polygons.length} объектами
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default App;
