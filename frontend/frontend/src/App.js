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
            console.log("WebSocket message received:", event.data);

            try {
                const data = JSON.parse(event.data);
                console.log("Parsed WebSocket data:", data);

                if (data.status === "invalid") {
                    setInvalidPolygons(prev => [...prev, data.intersecting_polygons]);
                    alert(`Ошибка: Полигон ${data.polygon.name} пересекается с другими`);
                }
            } catch (error) {
                console.error("Ошибка парсинга WebSocket-сообщения:", error);
            }
        };
        ws.onclose = () => console.log("WebSocket disconnected");
        setSocket(ws);

        return () => {
            ws.close();
        };
    }, []);

    const addPoint = () => {
        const lat = prompt('Введите широту:');
        if (lat === null) {
            alert("Ввод широты отменён. Точка не добавлена.");
            return;
        }

        const lng = prompt('Введите долготу:');
        if (lng === null) {
            alert("Ввод долготы отменён. Точка не добавлена.");
            return;
        }

        if (isNaN(parseFloat(lat))) {
            alert("Широта должна быть числом. Точка не добавлена.");
            return;
        }

        if (isNaN(parseFloat(lng))) {
            alert("Долгота должна быть числом. Точка не добавлена.");
            return;
        }

        const newPoint = [parseFloat(lat), parseFloat(lng)];
        setCoordinates([...coordinates, newPoint]);
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

    const parsePolygon = (wkt) => {
        const match = wkt.match(/POLYGON \(\((.+)\)\)/);
        if (!match) return [];
        return match[1].split(', ').map(coord => {
            const [lng, lat] = coord.split(' ').map(Number);
            return [lat, lng];
        });
    };

    const loadPolygons = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/polygons/');
            const transformedPolygons = response.data.results.map(polygon => ({
                ...polygon,
                coordinates: parsePolygon(polygon.coordinates),
            }));
            setPolygons(transformedPolygons);
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
                    <button type="button" onClick={() => addPoint()}>
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

            <h2>Список полигонов</h2>
            <table id="polygonTable">
                <thead>
                <tr>
                    <th>Название</th>
                    <th>Координаты</th>
                    <th>Пересекает антимеридиан</th>
                </tr>
                </thead>
                <tbody>
                    {polygons.map((polygon, index) => (
                        <tr key={index}>
                            <td>{polygon.name}</td>
                            <td>{JSON.stringify(polygon.coordinates)}</td>
                            <td>{polygon.crosses_antimeridian ? 'True' : 'False'}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default App;
