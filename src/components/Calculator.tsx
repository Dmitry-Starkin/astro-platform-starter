import React, { useState } from 'react';

const Calculator: React.FC = () => {
  const [display, setDisplay] = useState('0');
  const [previousValue, setPreviousValue] = useState<string | null>(null);
  const [operation, setOperation] = useState<string | null>(null);
  const [waitingForNewValue, setWaitingForNewValue] = useState(false);

  const inputNumber = (num: string) => {
    if (waitingForNewValue) {
      setDisplay(num);
      setWaitingForNewValue(false);
    } else {
      setDisplay(display === '0' ? num : display + num);
    }
  };

  const inputDot = () => {
    if (waitingForNewValue) {
      setDisplay('0.');
      setWaitingForNewValue(false);
    } else if (display.indexOf('.') === -1) {
      setDisplay(display + '.');
    }
  };

  const clear = () => {
    setDisplay('0');
    setPreviousValue(null);
    setOperation(null);
    setWaitingForNewValue(false);
  };

  const performOperation = (nextOperation: string) => {
    const inputValue = parseFloat(display);

    if (previousValue === null) {
      setPreviousValue(String(inputValue));
    } else if (operation) {
      const currentValue = previousValue || '0';
      const newValue = calculate(parseFloat(currentValue), inputValue, operation);

      setDisplay(`${parseFloat(newValue.toFixed(7))}`);
      setPreviousValue(`${newValue}`);
    }

    setWaitingForNewValue(true);
    setOperation(nextOperation);
  };

  const calculate = (firstValue: number, secondValue: number, operation: string): number => {
    switch (operation) {
      case '+':
        return firstValue + secondValue;
      case '-':
        return firstValue - secondValue;
      case '×':
        return firstValue * secondValue;
      case '÷':
        return firstValue / secondValue;
      case '=':
        return secondValue;
      default:
        return secondValue;
    }
  };

  const percentage = () => {
    const value = parseFloat(display) / 100;
    setDisplay(String(value));
  };

  const toggleSign = () => {
    const value = parseFloat(display);
    setDisplay(String(value * -1));
  };

  const Button: React.FC<{
    onClick: () => void;
    className?: string;
    children: React.ReactNode;
  }> = ({ onClick, className = '', children }) => (
    <button
      className={`h-16 text-xl font-semibold rounded-xl transition-all duration-200 hover:scale-105 active:scale-95 ${className}`}
      onClick={onClick}
    >
      {children}
    </button>
  );

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-gradient-to-br from-gray-900 to-gray-800 rounded-2xl shadow-2xl p-6">
        {/* Дисплей */}
        <div className="bg-black rounded-xl p-6 mb-6">
          <div className="text-right">
            <div className="text-gray-400 text-sm mb-1">
              {previousValue && operation && `${previousValue} ${operation}`}
            </div>
            <div className="text-white text-4xl font-light truncate">
              {display}
            </div>
          </div>
        </div>

        {/* Кнопки */}
        <div className="grid grid-cols-4 gap-3">
          {/* Первый ряд */}
          <Button
            onClick={clear}
            className="bg-gray-600 hover:bg-gray-500 text-white col-span-2"
          >
            Clear
          </Button>
          <Button
            onClick={toggleSign}
            className="bg-gray-600 hover:bg-gray-500 text-white"
          >
            +/-
          </Button>
          <Button
            onClick={percentage}
            className="bg-gray-600 hover:bg-gray-500 text-white"
          >
            %
          </Button>

          {/* Второй ряд */}
          <Button
            onClick={() => inputNumber('7')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            7
          </Button>
          <Button
            onClick={() => inputNumber('8')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            8
          </Button>
          <Button
            onClick={() => inputNumber('9')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            9
          </Button>
          <Button
            onClick={() => performOperation('÷')}
            className="bg-orange-500 hover:bg-orange-400 text-white"
          >
            ÷
          </Button>

          {/* Третий ряд */}
          <Button
            onClick={() => inputNumber('4')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            4
          </Button>
          <Button
            onClick={() => inputNumber('5')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            5
          </Button>
          <Button
            onClick={() => inputNumber('6')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            6
          </Button>
          <Button
            onClick={() => performOperation('×')}
            className="bg-orange-500 hover:bg-orange-400 text-white"
          >
            ×
          </Button>

          {/* Четвертый ряд */}
          <Button
            onClick={() => inputNumber('1')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            1
          </Button>
          <Button
            onClick={() => inputNumber('2')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            2
          </Button>
          <Button
            onClick={() => inputNumber('3')}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            3
          </Button>
          <Button
            onClick={() => performOperation('-')}
            className="bg-orange-500 hover:bg-orange-400 text-white"
          >
            -
          </Button>

          {/* Пятый ряд */}
          <Button
            onClick={() => inputNumber('0')}
            className="bg-gray-700 hover:bg-gray-600 text-white col-span-2"
          >
            0
          </Button>
          <Button
            onClick={inputDot}
            className="bg-gray-700 hover:bg-gray-600 text-white"
          >
            .
          </Button>
          <Button
            onClick={() => performOperation('+')}
            className="bg-orange-500 hover:bg-orange-400 text-white"
          >
            +
          </Button>

          {/* Кнопка равно */}
          <Button
            onClick={() => performOperation('=')}
            className="bg-orange-500 hover:bg-orange-400 text-white col-span-4 mt-3"
          >
            =
          </Button>
        </div>

        {/* История операций */}
        <div className="mt-6 text-center">
          <div className="text-gray-400 text-sm">
            Современный калькулятор с поддержкой базовых операций
          </div>
        </div>
      </div>
    </div>
  );
};

export default Calculator;