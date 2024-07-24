import React, { useEffect, useState } from "react";

const Items = () => {
    const [items, setItems] = useState([]);
    const [answers, setAnswers] = useState({});
    const [error, setError] = useState("");

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
            const response = await fetch(`http://localhost:8000/items/${id}/answer`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },
                body: JSON.stringify({ user_id: "some_user_id", answer: answers[id] })
            });

            if (response.ok) {
                alert("Respuesta enviada!");
                // Actualiza los items para mostrar la respuesta agregada
                const updatedItems = items.map(item => {
                    if (item.id === id) {
                        return { ...item, answers: [...item.answers, { user_id: "some_user_id", answer: answers[id] }] };
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

    return (
        <div className="items-container">
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
                            {item.answers.map((answer, index) => (
                                <li key={index}>{answer.answer}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default Items;
