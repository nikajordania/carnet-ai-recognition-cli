import asyncio
import aiohttp
import os
import zipfile

# Specify the endpoint URL
auto_page_n = lambda nth_page: f"https://api2.myauto.ge/ka/products?TypeID=0&ForRent=&Mans=&CurrencyID=3&MileageType=1&Page={nth_page}"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/58.0.3029.110 Safari/537.3"
}

async def download_image(session, url, save_directory):
    try:
        async with session.get(url) as response:
            response.raise_for_status()

            # Extract the filename from the URL
            filename = os.path.basename(url)

            # Save the image to the specified directory
            save_path = os.path.join(save_directory, filename)
            with open(save_path, 'wb') as file:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    file.write(chunk)

            print(f"Downloaded: {filename}")
    except aiohttp.ClientError as e:
        print(f"Error downloading image: {e}")


async def parse_myauto():
    image_urls = []  # List to store image URLs

    async with aiohttp.ClientSession(headers=headers) as session:
        for page_n in range(1):
            response = await session.get(auto_page_n(page_n))
            response.raise_for_status()

            data = await response.json()

            for item in data['data']['items']:
                car_id = item['car_id']
                photo = item['photo']
                picn = item['pic_number']
                print(f"Car ID: {car_id}")
                print("Image URLs:")
                for id in range(1, picn + 1):
                    image_url = f"https://static.my.ge/myauto/photos/{photo}/large/{car_id}_{id}.jpg"
                    image_urls.append(image_url)
                    print(image_url)
                print()

        # Create a folder to store downloaded images
        save_directory = "downloaded_images"
        os.makedirs(save_directory, exist_ok=True)

        # Download images asynchronously
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in image_urls:
                task = asyncio.ensure_future(download_image(session, url, save_directory))
                tasks.append(task)

            await asyncio.gather(*tasks)

        # Zip the downloaded images
        zip_filename = "downloaded_images.zip"
        with zipfile.ZipFile(zip_filename, 'w') as zip_file:
            for root, _, files in os.walk(save_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, arcname=file)

        print(f"\nAll images downloaded and zipped successfully.")
        zip_file_size_mb = os.path.getsize(zip_filename) / (1024 * 1024)
        print(f"ZIP file size: {zip_file_size_mb:.2f} MB")

        total_images = sum(len(files) for _, _, files in os.walk(save_directory))
        print(f"Total number of downloaded images: {total_images}")


def download_images():
    asyncio.run(parse_myauto())