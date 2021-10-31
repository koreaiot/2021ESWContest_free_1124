import numpy as np
import re
class UT:
    
    def load_labels(path='labels.txt'):
        """
        Date : 21.09.17
        Function : Loads the labels file. Supports files with or without index numbers.
        """
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            labels = {}
            for row_number, content in enumerate(lines):
                pair = re.split(r'[:\s]+', content.strip(), maxsplit=1)
                if len(pair) == 2 and pair[0].strip().isdigit():
                    labels[int(pair[0])] = pair[1].strip()
                else:
                    labels[row_number] = pair[0].strip()
        return labels


    def set_input_tensor(interpreter, image):
        """
        Date : 21.09.19
        Function : Sets the input tensor.
        """
        tensor_index = interpreter.get_input_details()[0]['index']
        input_tensor = interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = np.expand_dims((image-255)/255, axis=0)


    def get_output_tensor(interpreter, index):
        """
        Date : 21.09.20
        Function : Returns the output tensor at the given index.
        """        
        output_details = interpreter.get_output_details()[index]
        tensor = np.squeeze(interpreter.get_tensor(output_details['index']))
        return tensor


    def detect_objects(interpreter, image, threshold):
        """
        Date : 21.09.20
        Function : Returns a list of detection results, each a dictionary of object info.
        """            
        UT.set_input_tensor(interpreter, image)
        interpreter.invoke()
        # Get all output details
        boxes = UT.get_output_tensor(interpreter, 1)
        classes = UT.get_output_tensor(interpreter, 3)
        scores = UT.get_output_tensor(interpreter, 0)
        count = int(UT.get_output_tensor(interpreter, 2))
        results = []
        for i in range(count):
            if scores[i] >= threshold:
                result_tf = {
                    'bounding_box': boxes[i],
                    'class_id': classes[i],
                    'score': scores[i]
                }
                results.append(result_tf)
        return results