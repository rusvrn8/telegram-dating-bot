import cv2
import numpy as np

# Примеры изображений с контентом для взрослых
adult_image_paths = ["adult1.jpg", "adult2.jpg", "adult3.jpg"]

# Примеры изображений без контента для взрослых
non_adult_image_paths = ["non_adult1.jpg", "non_adult2.jpg", "non_adult3.jpg"]

# Обучение модели с использованием примеров изображений
data = []
labels = []

# Загружаем изображения и добавляем их в обучающий набор данных
for path in adult_image_paths:
    image = cv2.imread(path)
    data.append(image.flatten())
    labels.append(1)  # 1 - для изображений с контентом для взрослых

for path in non_adult_image_paths:
    image = cv2.imread(path)
    data.append(image.flatten())
    labels.append(0)  # 0 - для изображений без контента для взрослых

data = np.array(data, dtype=np.float32)
labels = np.array(labels)

# Обучение модели с использованием метода перцептрона
perceptron = cv2.ml.ANN_MLP.create()
perceptron.setLayerSizes(np.array([data.shape[1], 32, 2]))
perceptron.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)
perceptron.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM)
perceptron.setTermCriteria((cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.1))

perceptron.train(data, cv2.ml.ROW_SAMPLE, labels)

# Функция для проверки изображения на контент для взрослых
def check_for_adult_content(image_path):
    image = cv2.imread(image_path)
    flattened_image = image.flatten()
    flattened_image = np.array([flattened_image], dtype=np.float32)
    _, result = perceptron.predict(flattened_image)

    if result[0][0] == 1:
        return "Это изображение содержит контент для взрослых."
    else:
        return "Это изображение не содержит контента для взрослых."

# Пример использования функции для проверки изображения
result = check_for_adult_content("test_image.jpg")
print(result)