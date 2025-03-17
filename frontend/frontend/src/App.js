import React, { useState } from 'react';
import { MapContainer, TileLayer, Polygon, Marker } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';

const App = () => {
    const [name, setName] = useState('');
    const [coordinates, setCoordinates] = useState([]);
    const [polygons, setPolygons] = useState([]);

    const addPoint = () => {
        const lat = prompt('Введите широту:');
        const lng = prompt('Введите долготу:');
        if (lat && lng) {
            const newPoint = [parseFloat(lat), parseFloat(lng)];
            setCoordinates([...coordinates, newPoint]);
        }
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

    React.useEffect(() => {
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
                    <textarea
                        id="coordinates"
                        value={JSON.stringify(coordinates)}
                        readOnly
                        rows="4"
                    />
                </div>
                <div className="form-group">
                    <button type="button" onClick={addPoint}>
                        Добавить точку
                    </button>
                </div>
                <button type="submit">Сохранить</button>
            </form>

            <div id="map">
                <MapContainer center={[55.75, 37.61]} zoom={5} style={{ height: '400px', width: '100%' }}>
                    <TileLayer
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        attribution='© OpenStreetMap contributors'
                    />
                    {coordinates.map((point, index) => (
                        <Marker key={index} position={point} />
                    ))}
                    {polygons.map((polygon, index) => (
                        <Polygon key={index} positions={polygon.coordinates} />
                    ))}
                </MapContainer>
            </div>

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
                        <td>{polygon.crosses_antimeridian ? 'Да' : 'Нет'}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default App;
