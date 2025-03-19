import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Polygon, Marker } from 'react-leaflet';
import axios from 'axios';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

L.Marker.prototype.options.icon = DefaultIcon;

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

    const normalizeLongitude = (lng) => {
        if (lng > 180) {
            return lng - 360;
        } else if (lng < -180) {
            return lng + 360;
        }
        return lng;
    };

    const crossesAntimeridian = (coordinates) => {
        let minLng = 180;
        let maxLng = -180;

        coordinates.forEach(([lat, lng]) => {
            if (lng < minLng) minLng = lng;
            if (lng > maxLng) maxLng = lng;
        });

        return (maxLng - minLng) > 180;
    };

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

        const normalizeDecimal = (value) => {
            value = value.replace(/[^0-9.]/g, '.');

            const parts = value.split('.');
            if (parts.length > 1) {
                value = `${parts[0]}.${parts.slice(1).join('')}`;
            }

            return value;
        };

        const normalizedLat = normalizeDecimal(lat);
        const normalizedLng = normalizeDecimal(lng);

        if (isNaN(parseFloat(normalizedLat))) {
            alert("Широта должна быть числом. Точка не добавлена.");
            return;
        }

        if (isNaN(parseFloat(normalizedLng))) {
            alert("Долгота должна быть числом. Точка не добавлена.");
            return;
        }

        const isValidCoordinate = (value, min, max) => {
            const num = parseFloat(value);
            return !isNaN(num) && num >= min && num <= max;
        };

        if (!isValidCoordinate(normalizedLat, -90, 90)) {
            alert("Широта должна быть числом от -90 до 90. Точка не добавлена.");
            return;
        }

        if (!isValidCoordinate(normalizedLng, -360, 360)) {
            alert("Долгота должна быть числом от -360 до 360. Точка не добавлена.");
            return;
        }

        const newPoint = [parseFloat(normalizedLat), parseFloat(normalizedLng)];
        setCoordinates([...coordinates, newPoint]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        const normalizedCoordinates = coordinates.map(([lat, lng]) => [
            lat,
            normalizeLongitude(lng),
        ]);

        const crossesAntimeridianFlag = crossesAntimeridian(normalizedCoordinates);

        try {
            const response = await axios.post('http://localhost:8000/api/polygons/', {
                name,
                coordinates: normalizedCoordinates,
                crosses_antimeridian: crossesAntimeridianFlag,
            });

            setPolygons([...polygons, response.data]);
            setCoordinates([]);
            setName('');
        } catch (error) {
            console.error('Error submitting polygon:', error);
        }
    };

    const parseWKT = (wkt) => {
        const cleanedWkt = wkt.replace(/SRID=\d+;POLYGON \(\(/, '').replace(/\)\)$/, '');

        const coords = cleanedWkt.split(',').map(coord => {
            const [lng, lat] = coord.trim().split(' ').map(parseFloat);
            return [normalizeLongitude(lng), lat];
        });

        return coords;
    };

    const loadPolygons = async () => {
        try {
            const response = await axios.get('http://localhost:8000/api/polygons/');
            const transformedPolygons = response.data.results.map(polygon => ({
                ...polygon,
                coordinates: parseWKT(polygon.coordinates),
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
                {polygons.map((polygon, index) => (
                    <Polygon
                        key={index}
                        positions={polygon.coordinates}
                        color={polygon.crosses_antimeridian ? 'red' : 'blue'}
                    />
                ))}
                {invalidPolygons.map((polygon, index) => (
                    <Polygon
                        key={index}
                        positions={polygon.polygon.coordinates}
                        color="red"
                    />
                ))}
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
