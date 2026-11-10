import asyncio
import base64
import logging
import pymupdf

from mcp.server import MCPServer
from os import path
from typing import Any


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
mcp = MCPServer("pdf-reader")


@mcp.tool()
async def get_data_from_pdf(file_path: str) -> list[dict[str, Any]]:
    """
    Extracts text and images from each page of a PDF file.

    Args:
        file_path (str): The path to the PDF file.

    Returns:
        list[dict[str, Any]]: A list of dictionaries containing page number, text, and images for each page.
    """
    if not path.exists(file_path):
        logger.error("File does not exist: %s", file_path)
        return []

    logger.info("Reading PDF file: %s", file_path)
    doc = pymupdf.open(file_path)
    pages_data = []
    for i, page in enumerate(doc):
        if i == 17:
            pass
        try:
            data = {
                "page_no": i + 1,
                "text": page.get_text(),
                "images": []
            }

            for j, img in enumerate(page.get_images(full=True)):
                xref = img[0]

                img_dict = doc.extract_image(xref)
                data["images"].append({
                    "img_index": j,
                    "img_base64": base64.b64encode(img_dict["image"]).decode('ascii'),
                    "img_ext": img_dict["ext"]
                })

            pages_data.append(data)
        except Exception as e:
            logger.error("Error reading page %d: %s", i + 1, e)

    logger.info(f"Read {len(pages_data)} pages from PDF file: {file_path}")
    return pages_data


if __name__ == "__main__":
    # details = asyncio.run(get_data_from_pdf("./sample.pdf"))
    # print(len(details))
    mcp.run(transport='stdio')
