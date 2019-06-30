from PIL import Image


im = Image.open('test.jpg')
w,h = im.size
print(w,h)
im = im.resize((w*2,h*2))
im.save('test_re.jpg')
