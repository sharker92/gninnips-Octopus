'''Create image from training'''
# pylint: disable=line-too-long, import-error
# flake8: noqa: E501
from PIL import Image, ImageDraw, ImageFont
from src.classes import Entrenamiento, Saltos, CicloDeEntrenamiento
from src.read_csv import resource_path, save_path


def generate_image(training, fecha, titulo=''):
    '''Convert training to jpeg'''
    img_width = 3840
    img_length = 2160
    img = Image.new('RGB', (img_width, img_length), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font_title = ImageFont.truetype(
        resource_path("./images/HelveticaNeueBold.ttf"), 225)
    font_tot_time = ImageFont.truetype(
        resource_path("./images/HelveticaNeueBold.ttf"), 90)
    logo = Image.open(resource_path('./images/logo.jpeg'))
    size = (350, 350)
    logo.thumbnail(size)
    img.paste(logo, (0, 0))
    x_title = center_text(img_width, titulo, draw, font_title)
    draw.text((x_title, 0), titulo, 0, font=font_title)
    x_date = img_width - 540
    file_date = fecha.strftime("%d/%m/%Y")
    draw.text((x_date, 0), file_date, 0, font=font_tot_time)
    date_len = draw.textlength(file_date, font=font_tot_time)
    training_time = training.get_time()
    x_time = center_text(date_len, training_time,
                         draw, font_tot_time) + x_date
    draw.text((x_time, 90), training_time, 0, font=font_tot_time)
    lst_images = list()
    for i in range(1, 10):
        tmp_img = Image.open(resource_path(f'./images/{i}.png'))
        size = (270, 270)
        tmp_img.thumbnail(size)
        lst_images.append(tmp_img)

    draw_training(img, draw, training, lst_images)
    print('Imagen guardada en:')
    img.save(save_path(f'{fecha.strftime("%d-%m-%Y")}.jpg'))


def draw_training(img, draw, training, lst_images, eje_x=200, eje_y=380):
    '''Recursive drawing cycle'''
    margin_x = 200
    margin_y = 460
    img_limit = 3540
    box_size = 300
    font = ImageFont.truetype(resource_path(
        "./images/HelveticaNeueBold.ttf"), 75)
    bracket_font = ImageFont.truetype(
        resource_path("./images/HelveticaNeueRegular.ttf"), 450)
    for trng in training:
        if isinstance(trng, CicloDeEntrenamiento):
            eje_x += 30
            y_cntrd = 135
            draw.text((eje_x - 225, eje_y - y_cntrd), '[',
                      font=bracket_font, fill=(255, 0, 0), stroke_width=3)
            eje_x, eje_y = draw_training(
                img, draw, trng, lst_images, eje_x, eje_y)
            end_text = f']x{trng.get_reps()}'
            end_text_lngth = int(draw.textlength(end_text, font=bracket_font))
            if eje_x + end_text_lngth - 500 > img_limit:
                eje_x = margin_x
                eje_y += 460
            draw.text((eje_x - 60, eje_y - y_cntrd), end_text,
                      font=bracket_font, fill=(255, 0, 0), stroke_width=3)
            eje_x += int(end_text_lngth - 400)

        elif isinstance(trng, Entrenamiento):
            img.paste(lst_images[trng.get_training() - 1], (eje_x, eje_y))
            draw.text((eje_x - 160, eje_y + 75), f'{trng.get_hearth_rate()}%',
                      0, font=font)
            x_cntrd = center_text(
                box_size, trng.get_cadence(), draw, font)
            draw.text((eje_x + x_cntrd, eje_y - 90), trng.get_cadence(),
                      0, font=font)
            if isinstance(trng, Saltos):
                x_cntrd = center_text(
                    box_size, trng.get_time_str(), draw, font)
                draw.text((eje_x + x_cntrd, eje_y + 290),
                          trng.get_time_str(),  0, font=font)
                x_cntrd = center_text(
                    box_size, trng.get_num_jump(), draw, font)
                draw.text((eje_x + x_cntrd, eje_y + 90),
                          trng.get_num_jump(), 0, font=font)
            else:
                x_cntrd = center_text(
                    box_size, trng.get_tot_time_str(), draw, font)
                draw.text((eje_x + x_cntrd, eje_y + 290),
                          trng.get_tot_time_str(), 0, font=font)

        eje_x += 500
        if eje_x > img_limit:
            eje_x = margin_x
            eje_y += margin_y
    return eje_x, eje_y


def center_text(width, text, draw, font):
    '''returns location for center text'''
    centered_text_location = width/2 - draw.textlength(text, font=font)/2
    return centered_text_location
