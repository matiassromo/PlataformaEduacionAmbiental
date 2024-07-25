import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const Items = () => {
    const [items, setItems] = useState([]);
    const [answers, setAnswers] = useState({});
    const [error, setError] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        const fetchItems = async () => {
            try {
                const token = localStorage.getItem("token");
                const response = await fetch("http://localhost:8000/items", {
                    headers: {
                        "Authorization": `Bearer ${token}`
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setItems(data);
                } else {
                    setError("Error al cargar las preguntas");
                }
            } catch (error) {
                setError("Error al conectar con el servidor");
            }
        };

        fetchItems();
    }, []);

    const handleAnswerChange = (id, value) => {
        setAnswers({
            ...answers,
            [id]: value
        });
    };

    const handleSubmit = async (e, id) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/answers/${id}/answer`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ answer: answers[id] })
            });
    
            if (response.ok) {
                const data = await response.json();
                alert("Respuesta enviada!");
                // Actualiza los items para mostrar la respuesta agregada
                const updatedItems = items.map(item => {
                    if (item.id === id) {
                        return { ...item, answers: [...item.answers, { answer: answers[id], _id: data.answer._id }] };
                    }
                    return item;
                });
                setItems(updatedItems);
            } else {
                setError("Error al enviar la respuesta");
            }
        } catch (error) {
            setError("Error al conectar con el servidor");
        }
    };
    

    const handleDelete = async (itemId, answerId) => {
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/answers/${itemId}/answer/${answerId}`, {
                method: "DELETE",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            if (response.ok) {
                alert("Respuesta eliminada!");
                // Actualiza los items para eliminar la respuesta
                const updatedItems = items.map(item => {
                    if (item.id === itemId) {
                        return { ...item, answers: item.answers.filter(answer => answer._id !== answerId) };
                    }
                    return item;
                });
                setItems(updatedItems);
            } else {
                setError("Error al eliminar la respuesta");
            }
        } catch (error) {
            setError("Error al conectar con el servidor");
        }
    };

    const handleEdit = async (itemId, answerId, newAnswer) => {
        if (!newAnswer) return;
    
        try {
            const token = localStorage.getItem("token");
            const response = await fetch(`http://localhost:8000/answers/${itemId}/answer/${answerId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ answer: newAnswer })
            });
    
            if (response.ok) {
                const updatedItems = items.map(item => {
                    if (item.id === itemId) {
                        return {
                            ...item,
                            answers: item.answers.map(answer =>
                                answer._id === answerId ? { ...answer, answer: newAnswer } : answer
                            )
                        };
                    }
                    return item;
                });
                setItems(updatedItems);
            } else {
                setError("Error al editar la respuesta");
            }
        } catch (error) {
            setError("Error al conectar con el servidor");
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/login");
    };

    return (
        <div className="items-container">
            <button onClick={handleLogout}>Cerrar sesión</button>
            <h1 className="title-all">Plataforma de educación ambiental</h1>
            <h2>Preguntas</h2>
            {error && <p className="error">{error}</p>}
            {items.map(item => (
                <div key={item.id} className="item">
                    <p>{item.description}</p>
                    <form onSubmit={(e) => handleSubmit(e, item.id)}>
                        <input
                            type="text"
                            placeholder="Conteste la pregunta"
                            value={answers[item.id] || ""}
                            onChange={(e) => handleAnswerChange(item.id, e.target.value)}
                        />
                        <button type="submit">Enviar</button>
                    </form>
                    <div className="answers">
                        <h4>Respuestas:</h4>
                        <ul>
                            {item.answers.map((answer) => (
                                <li key={answer._id}>
                                    {answer.answer}
                                    <button onClick={() => handleEdit(item.id, answer._id, prompt("Edita tu respuesta", answer.answer))}>Editar</button>
                                    <button onClick={() => handleDelete(item.id, answer._id)}>Eliminar</button>
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default Items;
